from binance_service import DataColumns, getData
from median_renko import MedianRenko
from renko import Renko
import numpy as np

if __name__ == '__main__':
    df = getData()
    renko = MedianRenko(np.array(df[DataColumns.OPEN.value]), np.array(df[DataColumns.HIGH.value]), np.array(df[DataColumns.LOW.value]), np.array(df[DataColumns.CLOSE.value]), np.array(df[DataColumns.VOLUME.value]), df[DataColumns.OPEN_TIME_READABLE.value], df[DataColumns.OPEN_TIME.value])
    renko.plot()
    renko.test_strategy()
    # renko.save_bricks()
