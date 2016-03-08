import functools


def called_with(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        wrapped.called_with = args, kwargs
        return fn(*args, **kwargs)

    return wrapped
