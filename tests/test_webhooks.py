import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)
URL = "/webhooks/customer-events"
SECRET = "test-secret"


@pytest.fixture(autouse=True)
def set_secret(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET", SECRET)


def sign(body: bytes) -> str:
    return hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()


BODY = json.dumps({"event": "customer.created", "customer_id": 1}).encode()


def test_valid_signature():
    r = client.post(URL, content=BODY, headers={"X-Signature": sign(BODY)})
    assert r.status_code == 200
    assert r.json() == {"status": "accepted"}


def test_tampered_payload():
    tampered = json.dumps({"event": "customer.created", "customer_id": 999}).encode()
    r = client.post(URL, content=tampered, headers={"X-Signature": sign(BODY)})
    assert r.status_code == 401
    assert r.json() == {"detail": "Invalid signature"}


def test_missing_signature():
    r = client.post(URL, content=BODY)
    assert r.status_code == 401