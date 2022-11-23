import numpy as np

def get_ema(x, n):
    """
    Computes n period exponential moving average for x
    source: https://matplotlib.org/1.5.3/examples/pylab_examples/finance_work2.html
    """
    x = np.asarray(x)
    weights = np.exp(np.linspace(-1., 0., n))

    weights /= weights.sum()

    ema = np.convolve(x, weights, mode='full')[:len(x)]
    # do we want nan for the first n values?
    # a[:n] = a[n]
    ema[:n] = float("NAN")
    return ema
