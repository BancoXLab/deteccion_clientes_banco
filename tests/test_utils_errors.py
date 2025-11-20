import pytest
import importlib

import src.utils.log as log_mod


class _FakeLog:
    def __init__(self, *a, **k):
        pass

    def error(self, *a, **k):
        return None

    def info(self, *a, **k):
        return None

    def warn(self, *a, **k):
        return None


def test_handle_exceptions_default_and_reraise(monkeypatch):
    # Patch Log class before importing errors to avoid exc_info collision
    monkeypatch.setattr(log_mod, "Log", _FakeLog)
    import src.utils.errors as errors_mod
    importlib.reload(errors_mod)
    handle_exceptions = errors_mod.handle_exceptions

    @handle_exceptions(default=42, reraise=False)
    def f1():
        raise ValueError("err")

    assert f1() == 42

    @handle_exceptions(default=None, reraise=True)
    def f2():
        raise KeyError("k")

    with pytest.raises(KeyError):
        f2()


def test_handle_exceptions_with_sanitize_fn(monkeypatch):
    monkeypatch.setattr(log_mod, "Log", _FakeLog)
    import src.utils.errors as errors_mod
    importlib.reload(errors_mod)
    handle_exceptions = errors_mod.handle_exceptions

    calls = {}

    def san(args, kwargs):
        calls['s'] = True
        return {"sanitized": True}

    @handle_exceptions(default="ok", reraise=False, sanitize_fn=san)
    def fx():
        raise RuntimeError("boom")

    assert fx() == "ok"
    assert calls.get('s') is True
