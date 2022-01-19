from binance.enums import *
from binance.client import Client
import numpy as np
import pandas as pd
import os
from datetime import datetime
from enum import Enum
import credentials

client=Client(credentials.getBinanceKey(), credentials.getBinanceSecretKey())

TIME_INTERVAL = '1 week ago UTC'
CURRENCY_PAIR = 'BTCBUSD'
CANDLE_INTERVAL = Client.KLINE_INTERVAL_5MINUTE

class DataColumns(Enum):
    OPEN_TIME = 'open_time'
    OPEN_TIME_READABLE = 'open_time_readable'
    OPEN = 'open'
    HIGH = 'high'
    LOW = 'low'
    CLOSE = 'close'
    VOLUME = 'volume'
    CLOSE_TIME = 'close_time'
    CLOSE_TIME_READABLE = 'close_time_readable'

# [
#   [
#     1499040000000,      // Open time
#     "0.01634790",       // Open
#     "0.80000000",       // High
#     "0.01575800",       // Low
#     "0.01577100",       // Close
#     "148976.11427815",  // Volume
#     1499644799999,      // Close time
#     "2434.19055334",    // Quote asset volume
#     308,                // Number of trades
#     "1756.87402397",    // Taker buy base asset volume
#     "28.46694368",      // Taker buy quote asset volume
#     "17928899.62484339" // Ignore.
#   ]
# ]

def getData():
    if not os.path.isfile('./historical_data.csv'):
        historical_data = client.get_historical_klines(CURRENCY_PAIR, CANDLE_INTERVAL, TIME_INTERVAL)
        np_historical_data = np.array(historical_data)
        np_historical_data = np.delete(np_historical_data, range(7, 12), 1)
        df = pd.DataFrame(np_historical_data, columns=[DataColumns.OPEN_TIME.value, DataColumns.OPEN.value, DataColumns.HIGH.value, DataColumns.LOW.value, DataColumns.CLOSE.value, DataColumns.VOLUME.value, DataColumns.CLOSE_TIME.value])
        df[DataColumns.OPEN_TIME_READABLE.value] = df.apply(lambda row: datetime.fromtimestamp(float(row[DataColumns.OPEN_TIME.value])/1000), axis=1)
        df[DataColumns.CLOSE_TIME_READABLE.value] = df.apply(lambda row: datetime.fromtimestamp(float(row[DataColumns.CLOSE_TIME.value])/1000), axis=1)
        df.to_csv('./historical_data.csv')
    df = pd.read_table(
        './historical_data.csv',
        header=None,
        sep=',',
        names=[DataColumns.OPEN_TIME.value, DataColumns.OPEN.value, DataColumns.HIGH.value, DataColumns.LOW.value, DataColumns.CLOSE.value, DataColumns.VOLUME.value, DataColumns.CLOSE_TIME.value, DataColumns.OPEN_TIME_READABLE.value, DataColumns.CLOSE_TIME_READABLE.value]
    )
    df = df.iloc[1: , :]
    types_dict = {DataColumns.OPEN.value: float, DataColumns.HIGH.value: float, DataColumns.LOW.value: float, DataColumns.CLOSE.value: float, DataColumns.VOLUME.value: float}
    for col, col_type in types_dict.items():
        df[col] = df[col].astype(col_type)
    return df

    