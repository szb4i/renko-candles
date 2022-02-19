import math
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import talib
from plotly.subplots import make_subplots
from logger import write_log

ATR_TIME_PERIOD = 14
SMA_TIME_PERIOD = 9
CANDLE_PERIOD_FOR_ATR = 1
# for example: if candle interval is 1 min and you want to calculate ATR for 5 min candles -> CANDLE_PERIOD_FOR_ATR = 5

TRADE_QUANTITY=1
LEVERAGE=3.0
FEE = 0.0015
INTEREST_RATE = 0.0004

class Renko():
    def __init__(self, o, h, l, c, v, t) -> None:
        self.bricks = []
        # bricks: items: index, t, brick_open, brick_close, volume, last_brick_direction
        self.sma = []
        self.obv = []
        self.volume_in_brick = 0
        self.brick_open = o[0]
        self.last_brick_direction = None
        # self.last_brick_direction: 0->bearish, 1->bullish
        self.brick_size = self.__get_last_atr(h[0:ATR_TIME_PERIOD*(CANDLE_PERIOD_FOR_ATR+1):], l[0:ATR_TIME_PERIOD*(CANDLE_PERIOD_FOR_ATR+1):], c[0:ATR_TIME_PERIOD*(CANDLE_PERIOD_FOR_ATR+1):])
        self.prev_brick_size=0
        for i in range(ATR_TIME_PERIOD*(CANDLE_PERIOD_FOR_ATR+1), len(c)):
            self.__append_brick(o, h, l, c, v, t, i)        
        self.__set_sma()
        self.__set_obv()

    def append_brick(self, o, h, l, c, v, t, i):
        # call it when running live. appends brick (transforms it to brick if passes conditions), updates sma and obv also
        # returns true if new renko brick is added. false otherwise
        bricks_len = len(self.bricks)
        self.__append_brick(o, h, l, c, v, t, i)
        if bricks_len == len(self.bricks):
            return False
        self.__set_sma()
        self.__set_obv()
        return True

    def __append_brick(self, o, h, l, c, v, t, i):
        self.volume_in_brick += v[i]
        if l[i]<self.brick_open-self.brick_size:
            if None == self.last_brick_direction or (0 == self.last_brick_direction  and l[i]<self.brick_open-self.brick_size):
                self.last_brick_direction = 0
                self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_open-self.brick_size, self.volume_in_brick,self.last_brick_direction])
                self.brick_open = self.brick_open-self.brick_size
                self.prev_brick_size=self.brick_size
                self.brick_size = self.__get_last_atr(h[0:i:], l[0:i:], c[0:i:])
                self.volume_in_brick = 0
            elif 1 == self.last_brick_direction and l[i]<self.brick_open-self.prev_brick_size-self.brick_size:
                self.last_brick_direction = 0
                self.bricks.append([len(self.bricks), t[i], self.brick_open-self.prev_brick_size, self.brick_open-self.prev_brick_size-self.brick_size, self.volume_in_brick,self.last_brick_direction])
                self.brick_open = self.brick_open-self.prev_brick_size-self.brick_size
                self.prev_brick_size=self.brick_size
                self.brick_size = self.__get_last_atr(h[0:i:], l[0:i:], c[0:i:])
                self.volume_in_brick = 0
        elif h[i]>self.brick_open+self.brick_size:
            if None == self.last_brick_direction or (1 == self.last_brick_direction and h[i]>self.brick_open+self.brick_size):
                self.last_brick_direction = 1
                self.bricks.append([len(self.bricks), t[i], self.brick_open, self.brick_open+self.brick_size, self.volume_in_brick,self.last_brick_direction])
                self.brick_open = self.brick_open+self.brick_size
                self.prev_brick_size=self.brick_size
                self.brick_size = self.__get_last_atr(h[0:i:], l[0:i:], c[0:i:])
                self.volume_in_brick = 0
            elif 0 == self.last_brick_direction and h[i]>self.brick_open+self.prev_brick_size+self.brick_size:
                self.last_brick_direction = 1
                self.bricks.append([len(self.bricks), t[i], self.brick_open+self.prev_brick_size, self.brick_open+self.prev_brick_size+self.brick_size, self.volume_in_brick,self.last_brick_direction])
                self.brick_open = self.brick_open+self.prev_brick_size+self.brick_size
                self.prev_brick_size=self.brick_size
                self.brick_size = self.__get_last_atr(h[0:i:], l[0:i:], c[0:i:])
                self.volume_in_brick = 0

    def __set_sma(self):
        self.sma = talib.SMA(np.array(list(sub[3] for sub in self.bricks)), timeperiod=SMA_TIME_PERIOD)

    def __set_obv(self):
        self.obv = talib.OBV(np.array(list(sub[3] for sub in self.bricks)), np.array(list(sub[4] for sub in self.bricks)))

    def __get_last_atr(self, h, l, c):
        start_index = (len(h)%CANDLE_PERIOD_FOR_ATR)
        n_of_rows = (len(h)-start_index)//CANDLE_PERIOD_FOR_ATR
        high = np.array(h[start_index::]).reshape((n_of_rows, CANDLE_PERIOD_FOR_ATR)).max(axis=1)
        low = np.array(l[start_index::]).reshape((n_of_rows, CANDLE_PERIOD_FOR_ATR)).min(axis=1)
        close = c[start_index::CANDLE_PERIOD_FOR_ATR]
        atr = np.array(talib.ATR(high=high, low=low, close=close, timeperiod=ATR_TIME_PERIOD))
        return atr[-1]

    def plot(self):
        np_bricks = np.array(self.bricks)
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
                go.Candlestick(
                    x=np_bricks[:,1],
                    open=np_bricks[:,2],
                    high=np_bricks[:,2],
                    low=np_bricks[:,3],
                    close=np_bricks[:,3]
                ),
        )
        fig.add_trace(
                go.Scatter(
                    x=np_bricks[:,1],
                    y=self.sma,
                    hoverinfo='skip'
                )
        )
        fig.update_layout(xaxis_rangeslider_visible=False)
        fig.update_xaxes(type='category')
        fig.show()

    def test_strategy(self):
        buy_price = 0
        sell_price = 0
        profit = 1
        win_counter = 0
        loss_counter = 0
        in_long_position = False
        in_short_position = False
        for i in range(ATR_TIME_PERIOD*CANDLE_PERIOD_FOR_ATR+1, len(self.bricks)):
            if not in_long_position and not in_short_position and self.bricks[i][3]>self.sma[i] and self.obv[i]>self.obv[i-1] and self.bricks[i][5]==1:
                in_long_position = True
                buy_price = self.bricks[i][3]
                write_log(self.bricks[i][1], 'long_op', ['brick_cl'], [buy_price])
            elif in_long_position and self.bricks[i][3] < self.sma[i]:
                # profit *= (self.bricks[i][3]/buy_price-0.0015)
                fee=FEE*TRADE_QUANTITY*(2*LEVERAGE-1)*self.bricks[i][3]
                interest_rate = INTEREST_RATE*TRADE_QUANTITY*(2*LEVERAGE-1)*self.bricks[i][3]
                profit*=(1+((self.bricks[i][3]-buy_price)*TRADE_QUANTITY*LEVERAGE-fee-interest_rate)/(buy_price*TRADE_QUANTITY))
                if buy_price<self.bricks[i][3]:
                    win_counter += 1
                    write_log(self.bricks[i][1], 'long_wn', ['brick_cl', 'profit'], [self.bricks[i][3], profit])
                else:
                    loss_counter += 1
                    write_log(self.bricks[i][1], 'long_ls', ['brick_cl', 'profit'], [self.bricks[i][3], profit])
                in_long_position = False
            if not in_long_position and not in_short_position and self.bricks[i][3]<self.sma[i] and self.obv[i]<self.obv[i-1] and self.bricks[i][5]==0:
                in_short_position = True
                sell_price = self.bricks[i][3]
                write_log(self.bricks[i][1], 'shrt_op', ['brick_cl'], [sell_price])
            elif in_short_position and self.bricks[i][3] > self.sma[i]:
                # profit *= (sell_price/self.bricks[i][3]-0.0015)
                fee=FEE*TRADE_QUANTITY*(2*LEVERAGE-1)*sell_price
                interest_rate = INTEREST_RATE*TRADE_QUANTITY*(2*LEVERAGE-1)*self.bricks[i][3]
                profit*=(1+((sell_price-self.bricks[i][3])*TRADE_QUANTITY*LEVERAGE-fee-interest_rate)/(self.bricks[i][3]*TRADE_QUANTITY))
                if sell_price>self.bricks[i][3]:
                    win_counter += 1
                    write_log(self.bricks[i][1], 'shrt_wn', ['brick_cl', 'profit'], [self.bricks[i][3], profit])
                else:
                    loss_counter += 1
                    write_log(self.bricks[i][1], 'shrt_ls', ['brick_cl', 'profit'], [self.bricks[i][3], profit])
                in_short_position = False
        print('profit: ' + str(profit))
        print('win_counter: ' + str(win_counter))
        print('loss_counter: ' + str(loss_counter))
        if win_counter+loss_counter!=0: print("win rate {}".format(win_counter/(win_counter+loss_counter)))
        print('total number of positions : {}'.format(win_counter+loss_counter))

    def save_bricks(self):
        df=pd.DataFrame(self.bricks)
        df.drop([0,1,4],axis=1,inplace=True)
        df=df.round(2)
        df.to_csv('./bricks.csv')