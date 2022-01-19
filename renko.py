import math
import numpy as np
import plotly.graph_objects as go
import talib
from plotly.subplots import make_subplots
from logger import write_log

class Renko():
    def __init__(self, o, h, l, c, v, t) -> None:
        self.atr_time_period = 14
        self.sma_time_period = 9
        self.first_atr = abs(l[0]-h[0])
        # bricks: items: index, t, brick_open, brick_close, volume, last_brick_direction
        self.bricks = []
        self.sma = []
        self.obv = []
        self.volume_in_brick = 0
        self.brick_open = o[0]
        self.last_brick_direction = None
        # self.last_brick_direction: 0->bearish, 1->bullish
        self.brick_size = self.__get_last_atr(h[0:self.atr_time_period+1:], l[0:self.atr_time_period+1:], c[0:self.atr_time_period+1:])
        for i in range(self.atr_time_period+1, len(c)):
            self.__append_candle(o, h, l, c, v, t, i)        
        self.__set_sma()
        self.__set_obv()

    def append_candle(self, o, h, l, c, v, t, i):
        # call it when running live. appends candle (transforms it to brick if passes conditions), updates sma and obv also
        self.__append_candle(o, h, l, c, v, t, i)
        self.__set_sma()
        self.__set_obv()

    def plot(self):
        np_bricks = np.array(self.bricks)
        fig = make_subplots(rows=2, cols=1)
        fig.add_trace(
                go.Candlestick(
                    x=np_bricks[:,0],
                    open=np_bricks[:,2],
                    high=np_bricks[:,2],
                    low=np_bricks[:,3],
                    close=np_bricks[:,3],
                    hovertext=np_bricks[:,1]
                ),
            1, 1
        )
        fig.add_trace(
                go.Scatter(
                    x=np_bricks[:,0],
                    y=self.sma
                ),
            1, 1
        )
        fig.add_trace(
                go.Scatter(
                    x=np_bricks[:,0],
                    y=self.obv
                ),
            2, 1
        )
        fig.show()

    def test_strategy(self):
        buy_price = 0
        sell_price = 0
        profit = 1
        win_counter = 0
        loss_counter = 0
        brick_growth_in_position = 0
        in_long_position = False
        in_short_position = False
        for i in range(self.sma_time_period, len(self.bricks)):
            if not in_long_position and not in_short_position and self.bricks[i][3]>self.sma[i] and self.obv[i]>self.obv[i-1] and self.bricks[i][5]==1:
                in_long_position = True
                buy_price = self.bricks[i][3]
                write_log(self.bricks[i][1], 'long_op', [], [])
            elif in_long_position and self.bricks[i][3] < self.sma[i]:
                profit *= (self.bricks[i][3]/buy_price-0.0015)
                if buy_price<self.bricks[i][3]:
                    loss_counter += 1
                    write_log(self.bricks[i][1], 'long_lost', ['profit'], [profit])
                else:
                    win_counter += 1
                    write_log(self.bricks[i][1], 'long_won', ['profit'], [profit])
                in_long_position = False
            if not in_long_position and not in_short_position and self.bricks[i][3]<self.sma[i] and self.obv[i]<self.obv[i-1] and self.bricks[i][5]==0:
                in_short_position = True
                sell_price = self.bricks[i][3]
            elif in_short_position and self.bricks[i][3] > self.sma[i]:
                profit *= (sell_price/self.bricks[i][3]-0.0015)
                if sell_price<self.bricks[i][3]:
                    loss_counter += 1
                else:
                    win_counter += 1
                in_short_position = False
        print('profit: ' + str(profit))
        print('win_counter: ' + str(win_counter))
        print('loss_counter: ' + str(loss_counter))
        print("win rate {}".format(win_counter/(win_counter+loss_counter)))
        print('average position per day: {}'.format((win_counter+loss_counter)/30/12))

    def __append_candle(self, o, h, l, c, v, t, i):
        self.volume_in_brick += v[i]
        if c[i]>self.brick_open+self.brick_size:
            if None == self.last_brick_direction or (1 == self.last_brick_direction and c[i]>self.brick_open+self.brick_size):
                self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_open+self.brick_size, self.volume_in_brick,self.last_brick_direction])
                self.brick_open = self.brick_open+self.brick_size
                self.last_brick_direction = 1
                self.brick_size = self.__get_last_atr(h[0:self.atr_time_period+1:], l[0:self.atr_time_period+1:], c[0:self.atr_time_period+1:])
                self.volume_in_brick = 0
            elif 0 == self.last_brick_direction and c[i]>self.brick_open+self.brick_size*2:
                self.bricks.append([len(self.bricks), t[i], self.brick_open+self.brick_size, self.brick_open+self.brick_size*2, self.volume_in_brick,self.last_brick_direction])
                self.brick_open = self.brick_open+self.brick_size*2
                self.last_brick_direction = 1
                self.brick_size = self.__get_last_atr(h[0:self.atr_time_period+1:], l[0:self.atr_time_period+1:], c[0:self.atr_time_period+1:])
                self.volume_in_brick = 0
        elif c[i]<self.brick_open-self.brick_size:
            if None == self.last_brick_direction or (0 == self.last_brick_direction  and c[i]<self.brick_open-self.brick_size):
                self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_open-self.brick_size, self.volume_in_brick,self.last_brick_direction])
                self.brick_open = self.brick_open-self.brick_size
                self.last_brick_direction = 0
                self.brick_size = self.__get_last_atr(h[0:self.atr_time_period+1:], l[0:self.atr_time_period+1:], c[0:self.atr_time_period+1:])
                self.volume_in_brick = 0
            elif 1 == self.last_brick_direction and c[i]<self.brick_open-self.brick_size*2:
                self.bricks.append([len(self.bricks), t[i], self.brick_open-self.brick_size, self.brick_open-self.brick_size*2, self.volume_in_brick,self.last_brick_direction])
                self.brick_open = self.brick_open-self.brick_size*2
                self.last_brick_direction = 0
                self.brick_size = self.__get_last_atr(h[0:self.atr_time_period+1:], l[0:self.atr_time_period+1:], c[0:self.atr_time_period+1:])
                self.volume_in_brick = 0

    def __set_sma(self):
        self.sma = talib.SMA(np.array(list(sub[3] for sub in self.bricks)), timeperiod=self.sma_time_period)

    def __set_obv(self):
        self.obv = talib.OBV(np.array(list(sub[3] for sub in self.bricks)), np.array(list(sub[4] for sub in self.bricks)))

    def __get_last_atr(self, h, l, c):
        atr = np.array(talib.ATR(high=h, low=l, close=c, timeperiod=self.atr_time_period))
        return atr[-1]