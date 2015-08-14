import itertools

flatten = itertools.chain.from_iterable
pairs = lambda ls: zip(ls[::2], ls[1::2])

def ngrams(xs, n):
    if n <= 1:
        raise ValueError('n should be > 1')
    ts = itertools.tee(xs, n)
    for i, t in enumerate(ts[1:]):
        for _ in range(i + 1):
            next(t, None)
    return zip(*ts)
