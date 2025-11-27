import os

from src.utils.log import Log


def test_log_basic(tmp_path):
    logfile = tmp_path / "test.log"
    l = Log(name="testlogger", logfile=str(logfile), level=20)
    # calling methods should not raise
    l.info("hello", foo=1)
    l.warn("warn", foo=2)
    l.error("err", foo=3)
    # logfile should exist
    assert logfile.exists()
