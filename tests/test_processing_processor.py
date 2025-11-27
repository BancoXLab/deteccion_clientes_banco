import pandas as pd
import pytest

from src.processing.processor import ETLProcessor, Processor


def test_etlprocessor_type_error():
    p = ETLProcessor(expected_columns=["a", "b"])
    with pytest.raises(TypeError):
        p.process({"not": "a dataframe"})


def test_etlprocessor_missing_columns_and_duplicates(tmp_path):
    df = pd.DataFrame({"a": [1, 2, 2], "c": [3, 4, 4]})
    p = ETLProcessor(expected_columns=["a", "b"])
    out = p.process(df)
    # duplicates removed
    assert len(out) == 2
    # original columns preserved
    assert "a" in out.columns


def test_etlprocessor_missing_columns_logs_warning(monkeypatch):
    """Verify that ETLProcessor calls log.warn when expected columns are missing."""
    df = pd.DataFrame({"a": [1, 2], "c": [3, 4]})
    p = ETLProcessor(expected_columns=["a", "b"])
    
    # Mock the log.warn method to capture calls
    warn_calls = {}
    original_warn = p.log.warn
    def fake_warn(msg, **kwargs):
        warn_calls["called"] = True
        warn_calls["msg"] = msg
        warn_calls["kwargs"] = kwargs
    
    monkeypatch.setattr(p.log, "warn", fake_warn)
    out = p.process(df)
    
    # Verify warn was called when columns are missing
    assert warn_calls.get("called") is True
    assert "missing" in warn_calls.get("msg", "").lower()
    assert "b" in str(warn_calls.get("kwargs", {}))


def test_processor_run_handles_exception(monkeypatch):
    class Bad(Processor):
        def process(self, df):
            raise RuntimeError("boom")

    b = Bad(raise_on_error=False)
    res = b.run(pd.DataFrame({"x": [1]}))
    assert res is None

    b2 = Bad(raise_on_error=True)
    with pytest.raises(RuntimeError):
        b2.run(pd.DataFrame({"x": [1]}))
