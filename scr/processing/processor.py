
from scr.utils.log import Log

class Processor:
    def __init__(self):
        self.log = Log(self.__class__.__name__)

    def loggins(self, msg, **meta):
        self.log.info(msg, **meta)

    def process(self, df):
        self.loggins("start processing", rows=len(df))
        try:
            pass
        finally:
            self.loggins("end processing", rows=len(df))