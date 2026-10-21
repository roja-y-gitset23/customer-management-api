# Customer Management API

FastAPI service with customer CRUD, API-key authentication, HMAC-signed
webhooks, SQLAlchemy + Alembic migrations, and a pytest integration suite.

## Tech stack
FastAPI, SQLAlchemy, Alembic, Pydantic, PostgreSQL/SQLite, pytest, pytest-cov

## Project structure
```
customer-management-api/
├── src/            application code (routers, models, schemas, auth)
├── tests/          pytest integration tests
├── scripts/        webhook demo script
├── alembic/        database migrations
├── .env.example
├── pyproject.toml
└── requirements.txt
```

## Setup
```bash
git clone https://github.com/<your-username>/customer-management-api.git
cd customer-management-api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn src.main:app --reload
```
Interactive docs: http://127.0.0.1:8000/docs

## Environment variables
| Name | Purpose |
|---|---|
| DATABASE_URL | Database connection string |
| API_KEY | Value expected in the X-API-Key header |
| WEBHOOK_SECRET | Secret used to verify HMAC-SHA256 webhook signatures |

## Endpoints
| Method | Path | Auth | Responses |
|---|---|---|---|
| GET | /health | none | 200 |
| POST | /customers | X-API-Key | 201, 401, 409, 422 |
| GET | /customers?page=&per_page= | X-API-Key | 200, 401, 422 |
| GET | /customers/{id} | X-API-Key | 200, 401, 404, 422 |
| PUT | /customers/{id} | X-API-Key | 200, 401, 404, 409, 422 |
| DELETE | /customers/{id} | X-API-Key | 204, 401, 404 |
| POST | /webhooks/customer-events | X-Signature | 200, 400, 401 |

## Webhook signing
The signature is the hex HMAC-SHA256 of the raw request body, using
`WEBHOOK_SECRET`, sent in the `X-Signature` header.
Demo: `python scripts/send_webhook.py`

## Running the tests
Tests use TestClient and a separate in-memory SQLite database, so the real
database is never touched. Each test starts with empty tables.
```bash
pytest -v
pytest --cov=src --cov-report=term-missing
```

## Test results
24 tests passing, with about 100% coverage.

![Test report](docs/test-report.png)