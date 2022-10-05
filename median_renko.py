import numpy as np
import plotly.graph_objects as go
import talib
from plotly.subplots import make_subplots

ATR_TIME_PERIOD = 14
CANDLE_PERIOD_FOR_ATR = 5
# for example: if candle interval is 1 min and you want to calculate ATR for 5 min candles -> CANDLE_PERIOD_FOR_ATR = 5

GUPPY_START = 5
GUPPY_END = 60
GUPPY_STEP = 5

class MedianRenko():
    def __init__(self, o, h, l, c, v, t) -> None:
        # bricks: index, time, brick_open, brick_close, is_bullish
        self.bricks: list[list[float]] = []
        self.brick_open: float = o[0]
        self.brick_size: float = self.__get_last_atr(h[0:(ATR_TIME_PERIOD+1)*CANDLE_PERIOD_FOR_ATR], l[0:(ATR_TIME_PERIOD+1)*CANDLE_PERIOD_FOR_ATR], c[0:(ATR_TIME_PERIOD+1)*CANDLE_PERIOD_FOR_ATR])
        self.brick_up_level: float = self.brick_open + self.brick_size
        self.brick_down_level: float = self.brick_open - self.brick_size
        for i in range((ATR_TIME_PERIOD+1)*CANDLE_PERIOD_FOR_ATR, len(c)):
            self.__append_brick(o, h, l, c, v, t, i)      


    def __get_last_atr(self, h, l, c):
        start_index = (len(h)%CANDLE_PERIOD_FOR_ATR)
        n_of_rows = (len(h)-start_index)//CANDLE_PERIOD_FOR_ATR
        high = np.array(h[start_index:]).reshape((n_of_rows, CANDLE_PERIOD_FOR_ATR)).max(axis=1)
        low = np.array(l[start_index:]).reshape((n_of_rows, CANDLE_PERIOD_FOR_ATR)).min(axis=1)
        close = c[start_index::CANDLE_PERIOD_FOR_ATR]
        atr = np.array(talib.ATR(high=high, low=low, close=close, timeperiod=ATR_TIME_PERIOD))
        return atr[-1]

    def __append_brick(self, o, h, l, c, v, t, i):
        if 0 == len(self.bricks):
            if h[i] > self.brick_up_level:
                self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_up_level, True])
                self.brick_open = self.brick_open + self.brick_size/2
                self.brick_up_level = self.brick_open + self.brick_size
                self.brick_down_level = self.brick_open - self.brick_size
                self.__on_brick_up_level_hit(o, h, l, c, v, t, i)
            elif l[i] < self.brick_down_level:
                self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_down_level, False])
                self.brick_open = self.brick_open - self.brick_size/2
                self.brick_up_level = self.brick_open + self.brick_size
                self.brick_down_level = self.brick_open - self.brick_size
                self.__on_brick_down_level_hit(o, h, l, c, v, t, i)
        else:
            if h[i] > self.brick_up_level:
                self.__on_brick_up_level_hit(o, h, l, c, v, t, i)
            elif l[i] < self.brick_down_level:
                self.__on_brick_down_level_hit(o, h, l, c, v, t, i)

    def __on_brick_up_level_hit(self, o, h, l, c, v, t, i):
        # while: if multiple bricks are finished in a single candle
        while h[i] > self.brick_up_level:
            self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_up_level, True])
            self.brick_open = self.brick_open + self.brick_size/2
            self.brick_up_level = self.brick_open + self.brick_size
            self.brick_down_level = self.brick_open - self.brick_size
        self.brick_size = self.__get_last_atr(h[0:i], l[0:i], c[0:i])
        self.brick_up_level = self.brick_open + self.brick_size
        self.brick_down_level = self.brick_open - self.brick_size

    def __on_brick_down_level_hit(self, o, h, l, c, v, t, i):
        # while: if multiple bricks are finished in a single candle
        while l[i] < self.brick_down_level:
            self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_down_level, False])
            self.brick_open = self.brick_open - self.brick_size/2
            self.brick_up_level = self.brick_open + self.brick_size
            self.brick_down_level = self.brick_open - self.brick_size
        self.brick_size = self.__get_last_atr(h[0:i], l[0:i], c[0:i])
        self.brick_up_level = self.brick_open + self.brick_size
        self.brick_down_level = self.brick_open - self.brick_size

    def __get_np_guppy(self, np_bricks):
        guppy = []
        for i in range(GUPPY_START, GUPPY_END, GUPPY_STEP):
            ema = talib.EMA(np.array(np_bricks[:,3], dtype=float), timeperiod=int(i))
            guppy.append(ema)
        np_guppy = np.array(guppy)
        return np_guppy

    def plot(self):
        np_bricks = np.array(self.bricks)
        np_guppy = self.__get_np_guppy(np_bricks)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
                go.Candlestick(
                    x=np_bricks[:,0],
                    open=np_bricks[:,2],
                    high=np_bricks[:,2],
                    low=np_bricks[:,3],
                    close=np_bricks[:,3],
                    hovertext=np_bricks[:,1],
                ),
        )
        for i in range(0, np.shape(np_guppy)[0]):
            fig.add_trace(
                    go.Scatter(
                        x=np_bricks[:,0],
                        y=np_guppy[i],
                        hoverinfo='skip'
                    )
            )
        # fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_layout(hovermode="closest")
        fig.update_xaxes(type='category')
        fig.update_yaxes(fixedrange=False)
        fig.show()