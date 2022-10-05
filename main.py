from binance_service import DataColumns, getData
from renko import Renko
import numpy as np

if __name__ == '__main__':
    df = getData()
    renko = Renko(np.array(df[DataColumns.OPEN.value]), np.array(df[DataColumns.HIGH.value]), np.array(df[DataColumns.LOW.value]), np.array(df[DataColumns.CLOSE.value]), np.array(df[DataColumns.VOLUME.value]), df[DataColumns.OPEN_TIME_READABLE.value])
    renko.test_strategy()
    renko.plot()
    renko.save_bricks()
