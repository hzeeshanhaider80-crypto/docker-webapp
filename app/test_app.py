# Automated tests. The pipeline runs these FIRST; if any fails, nothing is deployed.
import app as app_module


def client():
    # Flask's built-in test client: calls the app without a real server.
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_health():
    # The health endpoint must return 200 and {"status": "ok"}.
    res = client().get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_home_shows_visits(monkeypatch):
    # Pretend Redis returned 42 (no real Redis needed in tests).
    monkeypatch.setattr(app_module, "get_visits", lambda: 42)
    res = client().get("/")
    assert res.status_code == 200
    assert b"42" in res.data


def test_home_without_redis(monkeypatch):
    # If Redis is down, the page must still load and show a friendly message.
    monkeypatch.setattr(app_module, "get_visits", lambda: None)
    res = client().get("/")
    assert b"Redis unavailable" in res.data
