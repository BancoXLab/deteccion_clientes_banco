import os
import importlib

def test_ops_db_init_and_save(tmp_path, monkeypatch):
    # For tests, set an in-memory SQLite DB before importing module
    monkeypatch.setenv("ALERTS_DB_URL", "sqlite:///:memory:")
    # reload module to pick up env var
    import src.ops.db as db
    importlib.reload(db)

    # Initialize DB (should create tables)
    db.init_db()

    # Save an alert
    a = db.save_alert("WARNING", "test message", "extra")
    assert hasattr(a, "id")
    assert a.level == "WARNING"
    assert "test" in a.message

    # Save a metric
    m = db.save_metric("test_metric", 3.14)
    assert hasattr(m, "id")
    assert m.name == "test_metric"
    assert abs(m.value - 3.14) < 1e-6
