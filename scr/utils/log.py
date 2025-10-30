import logging
from logging.handlers import RotatingFileHandler

class Log:
    def __init__(self, name=__name__, level=logging.INFO, logfile="/tmp/app.log"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self.logger.setLevel(level)
            fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
            sh = logging.StreamHandler()
            sh.setFormatter(fmt)
            fh = RotatingFileHandler(logfile, maxBytes=5*1024*1024, backupCount=3)
            fh.setFormatter(fmt)
            self.logger.addHandler(sh)
            self.logger.addHandler(fh)

    def info(self, msg, **kwargs):
        self.logger.info(msg, extra=kwargs)

    def warn(self, msg, **kwargs):
        self.logger.warning(msg, extra=kwargs)

    def error(self, msg, **kwargs):
        self.logger.error(msg, extra=kwargs)