from binance_service import DataColumns, getData
from renko import Renko

if __name__ == '__main__':
    df = getData()
    renko = Renko(df[DataColumns.OPEN.value], df[DataColumns.HIGH.value], df[DataColumns.LOW.value], df[DataColumns.CLOSE.value], df[DataColumns.VOLUME.value], df[DataColumns.OPEN_TIME_READABLE.value])
    renko.plot()