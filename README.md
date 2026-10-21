# Customer Management API

A FastAPI application for managing customer records, backed by PostgreSQL.

- **Task 1:** project setup, SQLAlchemy model, Alembic migration, Pydantic schemas, `GET /health`, DB session dependency
- **Task 2:** full CRUD endpoints protected by an `X-API-Key` header, pagination, `404` / `409` handling

## Tech stack

- Python 3.10+
- FastAPI and Uvicorn
- SQLAlchemy 2.x and Alembic (migrations)
- PostgreSQL (`psycopg2-binary`)
- Pydantic v2 (`pydantic[email]`)
- python-dotenv, pytest, httpx, requests

## Project structure

```
customer-crud-api/
├── src/
│   ├── __init__.py
│   ├── main.py            # FastAPI app, GET /health
│   ├── database.py        # engine, SessionLocal, Base, get_db dependency
│   ├── models.py          # Customer model
│   ├── schemas.py         # CustomerCreate, CustomerUpdate, CustomerOut, CustomerPage
│   ├── security.py        # X-API-Key dependency
│   └── routers/
│       ├── __init__.py
│       └── customers.py   # CRUD endpoints
├── scripts/
│   └── demo_client.py     # prints the expected Task 2 output
├── tests/
│   ├── __init__.py
│   └── test_health.py
├── alembic/               # migration environment and versions
├── alembic.ini
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## Setup (Windows PowerShell)

### 1. Clone and create a virtual environment

```powershell
git clone https://github.com/roja-y-gitset23/customer-management-api.git
cd customer-management-api
git checkout feature/customer-api

python -m venv venv
.\venv\Scripts\Activate.ps1
```

If activation is blocked, run `Set-ExecutionPolicy -Scope Process Bypass` first.

### 2. Install packages

```powershell
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary python-dotenv "pydantic[email]" pytest httpx requests
```

### 3. Create the PostgreSQL database

```powershell
psql -U postgres -c "CREATE DATABASE customer_db;"
```

If `psql` is not recognized, use its full path (for example `& "C:\Program Files\PostgreSQL\17\bin\psql.exe" ...`) or create the database in pgAdmin.

### 4. Configure environment variables

Copy the example file and edit the values:

```powershell
Copy-Item .env.example .env
notepad .env
```

`.env` contents:

```
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/customer_db
API_KEY=my-secret-key-123
```

Special characters in the password must be URL-encoded (`@` becomes `%40`). The `.env` file is ignored by Git. Only `.env.example` is committed.

### 5. Apply the database migration

```powershell
alembic upgrade head
```

This creates the `customers` table (and the `alembic_version` table). The migration file is in `alembic/versions/`.

### 6. Run the API

```powershell
uvicorn src.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs

## Database model

Table `customers`:

| Column     | Type                     | Notes              |
|------------|--------------------------|--------------------|
| id         | integer                  | primary key        |
| name       | varchar(100)             | required           |
| email      | varchar(255)             | required, unique   |
| phone      | varchar(20)              | optional           |
| city       | varchar(100)             | optional           |
| created_at | timestamp with time zone | set by the database |

## API endpoints

All `/customers` endpoints require the header `X-API-Key: <your API_KEY>`. `/health` is public.

| Method | Path                | Description                         | Success | Errors        |
|--------|---------------------|-------------------------------------|---------|---------------|
| GET    | `/health`           | Health check                        | 200     | n/a           |
| POST   | `/customers`        | Create a customer                   | 201     | 401, 409, 422 |
| GET    | `/customers`        | List customers (paginated)          | 200     | 401, 422      |
| GET    | `/customers/{id}`   | Get one customer                    | 200     | 401, 404      |
| PUT    | `/customers/{id}`   | Update a customer (partial allowed) | 200     | 401, 404, 409 |
| DELETE | `/customers/{id}`   | Delete a customer                   | 204     | 401, 404      |

Status code meanings:

- `401`: missing or invalid `X-API-Key`
- `404`: customer id not found
- `409`: email already exists
- `422`: invalid request body or query parameters

### Pagination

`GET /customers?page=1&per_page=10`

- `page`: starts at 1 (default 1)
- `per_page`: 1 to 100 (default 10)

Response:

```json
{
  "items": [
    {
      "id": 1,
      "name": "Asha",
      "email": "asha@example.com",
      "phone": "9876543210",
      "city": "Chennai",
      "created_at": "2026-10-21T10:00:00+05:30"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

### Example request

```powershell
curl.exe -X POST http://127.0.0.1:8000/customers `
  -H "X-API-Key: my-secret-key-123" `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"Asha\",\"email\":\"asha@example.com\",\"phone\":\"9876543210\",\"city\":\"Chennai\"}'
```

## Testing

### From Swagger UI (/docs)

1. Open http://127.0.0.1:8000/docs.
2. Click **Authorize**, enter your `API_KEY`, then **Authorize** and **Close**.
3. Try each endpoint:
   - `POST /customers` returns 201. Posting the same email again returns 409.
   - `GET /customers` with `page` and `per_page` returns 200.
   - `GET /customers/999` returns 404.
   - `PUT /customers/{id}` returns 200. `DELETE /customers/{id}` returns 204.
4. Click **Authorize**, then **Logout**, and call any customer endpoint to get 401.

### Demo script

With the server running, in a second terminal:

```powershell
python scripts\demo_client.py
```

Expected output:

```
POST /customers -> 201
GET /customers?page=1&per_page=10 -> 200
GET /customers/999 -> 404
No API key -> 401
```

### Automated tests

```powershell
pytest
```

## Git workflow

- `main`: base branch
- `feature/customer-api`: branch for this work

```powershell
git add .
git commit -m "Describe your change"
git push -u origin feature/customer-api
```

## Troubleshooting

- **`ModuleNotFoundError: No module named 'src'`:** run commands from the project root and check that `src/__init__.py` exists.
- **`database "customer_db" does not exist`:** create it (step 3), then run `alembic upgrade head` again.
- **Server ignores `.env` changes:** restart Uvicorn, because `.env` is read at startup.
- **`401` on every request:** the `X-API-Key` header must match `API_KEY` in `.env` exactly.