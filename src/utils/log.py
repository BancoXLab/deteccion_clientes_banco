import os
import logging
from logging.handlers import RotatingFileHandler


class Log:
    """Simple logger wrapper.

    - `logfile` and `level` can be configured via LOG_FILE and LOG_LEVEL env vars.
    """

    def __init__(self, name: str = __name__, level: int | None = None, logfile: str | None = None):
        # leer configuración desde env vars si no se pasan explícitamente
        env_logfile = os.getenv("LOG_FILE")
        env_level = os.getenv("LOG_LEVEL")

        if logfile is None:
            logfile = env_logfile or "/tmp/app.log"

        if level is None:
            # permitir valores por nombre (DEBUG/INFO/ERROR) o por int
            if env_level:
                level = getattr(logging, env_level.upper(), logging.INFO)
            else:
                level = logging.INFO

        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self.logger.setLevel(level)
            fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
            sh = logging.StreamHandler()
            sh.setFormatter(fmt)
            fh = RotatingFileHandler(logfile, maxBytes=5 * 1024 * 1024, backupCount=3)
            fh.setFormatter(fmt)
            self.logger.addHandler(sh)
            self.logger.addHandler(fh)

    def info(self, msg, **kwargs):
        extra = self._sanitize_extra(kwargs)
        exc_info = kwargs.pop("exc_info", None)
        self.logger.info(msg, extra=extra, exc_info=exc_info)

    def warn(self, msg, **kwargs):
        extra = self._sanitize_extra(kwargs)
        exc_info = kwargs.pop("exc_info", None)
        self.logger.warning(msg, extra=extra, exc_info=exc_info)

    def error(self, msg, **kwargs):
        extra = self._sanitize_extra(kwargs)
        exc_info = kwargs.pop("exc_info", None)
        self.logger.error(msg, extra=extra, exc_info=exc_info)

    def _sanitize_extra(self, kwargs: dict) -> dict:
        """Remove keys that would conflict with LogRecord attributes and return a safe `extra` dict.

        Also leaves the original kwargs untouched for extraction of `exc_info` by callers.
        """
        # Keys reserved by LogRecord - passing them in `extra` raises KeyError
        reserved = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
            'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
            'created', 'msecs', 'relativeCreated', 'thread', 'threadName', 'processName', 'process'
        }
        return {k: v for k, v in kwargs.items() if k not in reserved}

    