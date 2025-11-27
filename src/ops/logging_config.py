import logging
import os
try:
    # Newer versions expose `pythonjsonlogger.json` while older expose `pythonjsonlogger.jsonlogger`
    try:
        from pythonjsonlogger import json as jsonlogger
    except Exception:
        from pythonjsonlogger import jsonlogger
except Exception:
    jsonlogger = None

def configure_logging(level: str = None):
    level = level or os.getenv("LOG_LEVEL", "INFO")
    logger = logging.getLogger()
    # avoid adding duplicate handlers during imports
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = os.getenv("LOG_FORMAT", "%(asctime)s %(name)s %(levelname)s %(message)s")
        if jsonlogger:
            formatter = jsonlogger.JsonFormatter(fmt)
        else:
            formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
