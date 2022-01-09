import numpy as np
import plotly.graph_objects as go
import talib
from plotly.subplots import make_subplots

class Renko():
    def __init__(self, c, t, size=2500) -> None:
        self.size = size
        # self.bricks array items in respective order:
        # index, time, brick_open, brick_close
        self.bricks = []
        brick_open = c[0]//self.size
        last_brick_direction = None
        # last_brick_direction: 0->bearish, 1->bullish
        for i in range(1, len(c)):    
            if c[i]>brick_open+self.size:
                if None == last_brick_direction or (1 == last_brick_direction and c[i]>brick_open+self.size):
                    self.bricks.append([i, t[i], brick_open, brick_open+self.size])
                    brick_open = brick_open+self.size
                    last_brick_direction = 1
                elif 0 == last_brick_direction and c[i]>brick_open+self.size*2:
                    self.bricks.append([i, t[i], brick_open+self.size, brick_open+self.size*2])
                    brick_open = brick_open+self.size*2
                    last_brick_direction = 1
            elif c[i]<brick_open-self.size:
                if None == last_brick_direction or (0 == last_brick_direction  and c[i]<brick_open-self.size):
                    self.bricks.append([i, t[i], brick_open, brick_open-self.size])
                    brick_open = brick_open-self.size
                    last_brick_direction = 0
                elif 1 == last_brick_direction and c[i]<brick_open-self.size*2:
                    self.bricks.append([i, t[i], brick_open-self.size, brick_open-self.size*2])
                    brick_open = brick_open-self.size*2
                    last_brick_direction = 0
        self.bricks = np.array(self.bricks)

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
        fig.show()