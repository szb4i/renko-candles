import numpy as np
import plotly.graph_objects as go
import talib
from plotly.subplots import make_subplots

class Renko():
    def __init__(self, o, h, l, c, v, t) -> None:
        self.atr_time_period = 14
        self.first_atr = abs(l[0]-h[0])
        # bricks: items: x, t, brick_open, brick_close, 
        self.bricks = []
        volume = 0
        brick_open = o[0]
        last_brick_direction = None
        # last_brick_direction: 0->bearish, 1->bullish
        brick_size = self.__get_last_atr(h[0:self.atr_time_period+1:], l[0:self.atr_time_period+1:], c[0:self.atr_time_period+1:])
        for i in range(self.atr_time_period+1, len(c)):    
            volume += v[i]
            if c[i]>brick_open+brick_size:
                if None == last_brick_direction or (1 == last_brick_direction and c[i]>brick_open+brick_size):
                    self.bricks.append([i, t[i], brick_open, brick_open+brick_size, volume])
                    brick_open = brick_open+brick_size
                    last_brick_direction = 1
                    brick_size = self.__get_last_atr(h[0:self.atr_time_period+1:], l[0:self.atr_time_period+1:], c[0:self.atr_time_period+1:])
                    volume = 0
                elif 0 == last_brick_direction and c[i]>brick_open+brick_size*2:
                    self.bricks.append([i, t[i], brick_open+brick_size, brick_open+brick_size*2, volume])
                    brick_open = brick_open+brick_size*2
                    last_brick_direction = 1
                    brick_size = self.__get_last_atr(h[0:self.atr_time_period+1:], l[0:self.atr_time_period+1:], c[0:self.atr_time_period+1:])
                    volume = 0
            elif c[i]<brick_open-brick_size:
                if None == last_brick_direction or (0 == last_brick_direction  and c[i]<brick_open-brick_size):
                    self.bricks.append([i, t[i], brick_open, brick_open-brick_size, volume])
                    brick_open = brick_open-brick_size
                    last_brick_direction = 0
                    brick_size = self.__get_last_atr(h[0:self.atr_time_period+1:], l[0:self.atr_time_period+1:], c[0:self.atr_time_period+1:])
                    volume = 0
                elif 1 == last_brick_direction and c[i]<brick_open-brick_size*2:
                    self.bricks.append([i, t[i], brick_open-brick_size, brick_open-brick_size*2, volume])
                    brick_open = brick_open-brick_size*2
                    last_brick_direction = 0
                    brick_size = self.__get_last_atr(h[0:self.atr_time_period+1:], l[0:self.atr_time_period+1:], c[0:self.atr_time_period+1:])
                    volume = 0
        self.bricks = np.array(self.bricks)
        self.sma = talib.SMA(self.bricks[:,3].astype(np.double), timeperiod=10)
        self.obv = talib.OBV(self.bricks[:,3].astype(np.double), self.bricks[:,4].astype(np.double))

    def __get_last_atr(self, h, l, c):
        atr = np.array(talib.ATR(high=h, low=l, close=c, timeperiod=self.atr_time_period))
        return atr[-1]

    def plot(self):
        fig = make_subplots(rows=2, cols=1)
        fig.add_trace(
                go.Candlestick(
                    x=self.bricks[:,0],
                    open=self.bricks[:,2],
                    high=self.bricks[:,2],
                    low=self.bricks[:,3],
                    close=self.bricks[:,3],
                    hovertext=self.bricks[:,1]
                ),
            1, 1
        )
        fig.add_trace(
                go.Scatter(
                    x=self.bricks[:,0],
                    y=self.sma
                ),
            1, 1
        )
        fig.add_trace(
                go.Scatter(
                    x=self.bricks[:,0],
                    y=self.obv
                ),
            2, 1
        )
        fig.show()