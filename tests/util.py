from decorator import decorator


@decorator
def called_with(fn, *args, **kwargs):
    result = fn(*args, **kwargs)
    fn.called_with = args, kwargs
    return result
