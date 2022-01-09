from binance_service import DataColumns, getData
from renko import Renko

if __name__ == '__main__':
    df = getData()
    renko = Renko(df[DataColumns.CLOSE.value], df[DataColumns.OPEN_TIME_READABLE.value])
    renko.plot()