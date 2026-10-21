from src.database import get_db


def test_health_returns_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_get_db_opens_and_closes_session():
    gen = get_db()
    db = next(gen)
    assert db is not None
    gen.close()