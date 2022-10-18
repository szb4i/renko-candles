from time import time
from typing import TypedDict
import numpy as np
import plotly.graph_objects as go
import talib
from plotly.subplots import make_subplots
from logger import write_log
import pandas as pd
from datetime import datetime

ATR_TIME_PERIOD = 5
CANDLE_PERIOD_FOR_ATR = 1
# for example: if candle interval is 1 min and you want to calculate ATR for 5 min candles -> CANDLE_PERIOD_FOR_ATR = 5

GUPPY_START = 30
GUPPY_END = 60
GUPPY_STEP = 5

class IAction(TypedDict):
    time: float
    event: str

class MedianRenko():
    def __init__(self, o, h, l, c, v, t, t_ms) -> None:
        # bricks: index, time, brick_open, brick_close, is_bullish, low
        self.bricks: list[list[float]] = []
        self.brick_open: float = o[0]
        self.brick_size: float = self.__get_last_atr(h[0:(ATR_TIME_PERIOD+1)*CANDLE_PERIOD_FOR_ATR], l[0:(ATR_TIME_PERIOD+1)*CANDLE_PERIOD_FOR_ATR], c[0:(ATR_TIME_PERIOD+1)*CANDLE_PERIOD_FOR_ATR])
        self.brick_up_level: float = self.brick_open + self.brick_size
        self.brick_down_level: float = self.brick_open - self.brick_size
        self.brick_low: float = 1000000.
        self.brick_high: float = 0.
        self.actions: list[IAction] = []
        for i in range((ATR_TIME_PERIOD+1)*CANDLE_PERIOD_FOR_ATR, len(c)):
            self.__append_brick(o, h, l, c, v, t, t_ms, i)      
        self.np_bricks = np.array(self.bricks)
        self.np_guppy = self.__get_np_guppy()


    def __get_last_atr(self, h, l, c):
        start_index = (len(h)%CANDLE_PERIOD_FOR_ATR)
        n_of_rows = (len(h)-start_index)//CANDLE_PERIOD_FOR_ATR
        high = np.array(h[start_index:]).reshape((n_of_rows, CANDLE_PERIOD_FOR_ATR)).max(axis=1)
        low = np.array(l[start_index:]).reshape((n_of_rows, CANDLE_PERIOD_FOR_ATR)).min(axis=1)
        close = c[start_index::CANDLE_PERIOD_FOR_ATR]
        atr = np.array(talib.ATR(high=high, low=low, close=close, timeperiod=ATR_TIME_PERIOD))
        return atr[-1]

    def __append_brick(self, o, h, l, c, v, t, t_ms, i):
        if l[i] < self.brick_low:
            self.brick_low = l[i]
        if h[i] > self.brick_high:
            self.brick_high = h[i]
        if 0 == len(self.bricks):
            if h[i] > self.brick_up_level:
                self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_up_level, 1, self.brick_low, self.brick_high, t_ms[i]])
                self.brick_open = self.brick_open + self.brick_size/2
                self.brick_up_level = self.brick_open + self.brick_size
                self.brick_down_level = self.brick_open - self.brick_size
                self.__on_brick_up_level_hit(o, h, l, c, v, t, t_ms, i)
            elif l[i] < self.brick_down_level:
                self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_down_level, 0, self.brick_low, self.brick_high, t_ms[i]])
                self.brick_open = self.brick_open - self.brick_size/2
                self.brick_up_level = self.brick_open + self.brick_size
                self.brick_down_level = self.brick_open - self.brick_size
                self.__on_brick_down_level_hit(o, h, l, c, v, t, t_ms, i)
        else:
            if h[i] > self.brick_up_level:
                self.__on_brick_up_level_hit(o, h, l, c, v, t, t_ms, i)
            elif l[i] < self.brick_down_level:
                self.__on_brick_down_level_hit(o, h, l, c, v, t, t_ms, i)

    def __on_brick_up_level_hit(self, o, h, l, c, v, t, t_ms, i):
        # while: if multiple bricks are finished in a single candle
        while h[i] > self.brick_up_level:
            self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_up_level, 1, self.brick_low, self.brick_high, t_ms[i]])
            self.brick_open = self.brick_open + self.brick_size/2
            self.brick_up_level = self.brick_open + self.brick_size
            self.brick_down_level = self.brick_open - self.brick_size
        self.brick_size = self.__get_last_atr(h[0:i], l[0:i], c[0:i])
        self.brick_up_level = self.brick_open + self.brick_size
        self.brick_down_level = self.brick_open - self.brick_size
        self.brick_low = 1000000.
        self.brick_high = 0.

    def __on_brick_down_level_hit(self, o, h, l, c, v, t, t_ms, i):
        # while: if multiple bricks are finished in a single candle
        while l[i] < self.brick_down_level:
            self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_down_level, 0, self.brick_low, self.brick_high, t_ms[i]])
            self.brick_open = self.brick_open - self.brick_size/2
            self.brick_up_level = self.brick_open + self.brick_size
            self.brick_down_level = self.brick_open - self.brick_size
        self.brick_size = self.__get_last_atr(h[0:i], l[0:i], c[0:i])
        self.brick_up_level = self.brick_open + self.brick_size
        self.brick_down_level = self.brick_open - self.brick_size
        self.brick_low = 1000000.
        self.brick_high = 0.

    def __get_np_guppy(self):
        guppy = []
        for i in range(GUPPY_START, GUPPY_END, GUPPY_STEP):
            ema = talib.EMA(np.array(self.np_bricks[:,3], dtype=float), timeperiod=int(i))
            guppy.append(ema)
        return np.array(guppy)

    def plot(self):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
                go.Candlestick(
                    x=self.np_bricks[:,0],
                    open=self.np_bricks[:,2],
                    high=self.np_bricks[:,2],
                    low=self.np_bricks[:,5],
                    close=self.np_bricks[:,3],
                    hovertext=self.np_bricks[:,1],
                ),
        )
        for i in range(0, np.shape(self.np_guppy)[0]):
            fig.add_trace(
                    go.Scatter(
                        x=self.np_bricks[:,0],
                        y=self.np_guppy[i],
                        hoverinfo='skip'
                    )
            )
        # fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_layout(hovermode="closest")
        fig.update_xaxes(type='category')
        fig.update_yaxes(fixedrange=False)
        fig.show()

    def test_strategy(self):
        in_long = False
        in_short = False
        tp = None
        sl = None
        for i in range(50, len(self.bricks)):
            if not in_long and not in_short  and self.__is_guppy_long_ok(i) and self.__is_brick_pattern_long_ok(i):
                low = float(self.np_bricks[i, 5]) if float(self.np_bricks[i, 5]) < float(self.np_bricks[i-1, 5]) else float(self.np_bricks[i-1, 5])
                sl = low
                tp = 2*float(self.np_bricks[i, 3]) - low
                in_long = True
                write_log(self.bricks[i][1], 'long_open', [], [])
                self.actions.append({ 'time': self.bricks[i][7], 'event': 'long_open' })
            elif in_long and float(self.np_bricks[i, 5]) < sl:
                in_long = False
                write_log(self.bricks[i][1], 'long_lost', [], [])
                self.actions.append({ 'time': self.bricks[i][7], 'event': 'long_lost' })
            elif in_long and float(self.np_bricks[i, 6]) > tp:
                in_long = False
                write_log(self.bricks[i][1], 'long_won', [], [])
                self.actions.append({ 'time': self.bricks[i][7], 'event': 'long_won' })
            
            if not in_short and not in_long  and self.__is_guppy_short_ok(i) and self.__is_brick_pattern_short_ok(i):
                high = float(self.np_bricks[i, 6]) if float(self.np_bricks[i, 6]) > float(self.np_bricks[i-1, 6]) else float(self.np_bricks[i-1, 6])
                sl = high
                tp = 2*float(self.np_bricks[i, 3]) - high
                in_short = True
                write_log(self.bricks[i][1], 'short_open', [], [])
                self.actions.append({ 'time': self.bricks[i][7], 'event': 'short_open' })
            elif in_short and float(self.np_bricks[i, 6]) > sl:
                in_short = False
                write_log(self.bricks[i][1], 'short_lost', [], [])
                self.actions.append({ 'time': self.bricks[i][7], 'event': 'short_lost' })
            elif in_short and float(self.np_bricks[i, 5]) < tp:
                in_short = False
                write_log(self.bricks[i][1], 'short_won', [], [])
                self.actions.append({ 'time': self.bricks[i][7], 'event': 'short_won' })
        df = pd.DataFrame.from_dict(self.actions)
        df['time'] = df.apply(lambda row: datetime.fromtimestamp(float(row['time'])/1000), axis=1)
        df.to_excel('test.xlsx', index=False)


    def __is_guppy_long_ok(self, i: int):
        for row in range(0, np.shape(self.np_guppy)[0]-1):
            if self.np_guppy[row, i] < self.np_guppy[row+1, i]:
                return False
        for row in range(0, np.shape(self.np_guppy)[0]-1):
            if self.np_guppy[row, i] - self.np_guppy[row, i-1] < 0:
                return False
        return True

    def __is_guppy_short_ok(self, i: int):
        for row in range(0, np.shape(self.np_guppy)[0]-1):
            if self.np_guppy[row, i] > self.np_guppy[row+1, i]:
                return False
        for row in range(0, np.shape(self.np_guppy)[0]-1):
            if self.np_guppy[row, i] - self.np_guppy[row, i-1] > 0:
                return False
        return True

    def __is_brick_pattern_long_ok(self, i: int):
        return 0 == int(self.np_bricks[i-1, 4]) and 1 == int(self.np_bricks[i, 4]) and self.np_bricks[i, 1] != self.np_bricks[i+1, 1]

    def __is_brick_pattern_short_ok(self, i: int):
        return 1 == int(self.np_bricks[i-1, 4]) and 0 == int(self.np_bricks[i, 4]) and self.np_bricks[i, 1] != self.np_bricks[i+1, 1]
