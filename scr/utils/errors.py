import functools
from scr.utils.log import Log

def handle_exceptions(default=None, reraise=False):
    log = Log("errors")
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                log.error("unhandled exception", exc_info=True, fn=fn.__name__, err=str(e))
                if reraise:
                    raise
                return default
        return wrapper
    return decorator