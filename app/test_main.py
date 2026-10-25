from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "alive"}


def test_readiness():
    r = client.get("/readyz")
    assert r.status_code == 200
    assert r.json() == {"status": "ready"}


def test_status_exposes_version_and_uptime():
    body = client.get("/status").json()
    assert body["status"] == "ok"
    assert body["version"] == "dev"
    assert body["uptime_seconds"] >= 0


def test_root():
    r = client.get("/")
    assert r.status_code == 200


def test_metrics_exposed():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text


def test_hash_endpoint():
    r = client.get("/api/hash", params={"text": "smoke", "algo": "sha256"})
    assert r.status_code == 200
    assert r.json()["hash"] == (
        "04d588cb41b8022d1233924f0fe8280d9e2bb92cdc81658eb102ef9c42fc9452"
    )


def test_password_token_length_is_bounded():
    r = client.get("/api/token", params={"kind": "password", "length": 64})
    assert r.status_code == 200
    assert len(r.json()["token"]) == 64

    rejected = client.get(
        "/api/token", params={"kind": "password", "length": 129}
    )
    assert rejected.status_code == 422
