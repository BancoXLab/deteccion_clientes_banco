import pytest
import importlib

import src.ops.notify as notify

def test_notify_slack_success(monkeypatch):
    called = {}
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "http://fake-url")
    import src.ops.notify as notify_mod
    importlib.reload(notify_mod)
    def fake_post(url, json, timeout):
        called["url"] = url
        called["json"] = json
        called["timeout"] = timeout
        class Resp:
            def raise_for_status(self):
                return None
        return Resp()
    monkeypatch.setattr(notify_mod.requests, "post", fake_post)
    result = notify_mod.notify_slack("test message")
    assert result is True
    assert called["url"] == "http://fake-url"
    assert called["json"] == {"text": "test message"}

def test_notify_slack_no_webhook(monkeypatch):
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    import src.ops.notify as notify_mod
    importlib.reload(notify_mod)
    result = notify_mod.notify_slack("test message")
    assert result is False

def test_notify_email_success(monkeypatch):
    monkeypatch.setenv("ALERTS_EMAIL", "test@example.com")
    import src.ops.notify as notify_mod
    importlib.reload(notify_mod)
    result = notify_mod.notify_email("subject", "body")
    assert result is True

def test_notify_email_no_email(monkeypatch):
    monkeypatch.delenv("ALERTS_EMAIL", raising=False)
    import src.ops.notify as notify_mod
    importlib.reload(notify_mod)
    result = notify_mod.notify_email("subject", "body")
    assert result is False