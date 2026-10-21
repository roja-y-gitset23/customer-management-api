import os

# Must be set BEFORE importing the app, so tests never touch the real database
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["API_KEY"] = "test-api-key"
os.environ["WEBHOOK_SECRET"] = "test-webhook-secret"

import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database import Base, get_db
from src.main import app

# Separate in-memory test database
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


def sign(body: bytes, secret: str = "test-webhook-secret") -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


@pytest.fixture(autouse=True)
def setup_db():
    """Fresh empty tables for every test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    return {"X-API-Key": "test-api-key"}


@pytest.fixture
def sample_customer():
    return {
        "name": "Asha Raman",
        "email": "asha@example.com",
        "phone": "9876543210",
        "city": "Chennai",
    }


@pytest.fixture
def signed_webhook():
    body = json.dumps({"event": "customer.created", "customer_id": 1}).encode()
    return body, sign(body)