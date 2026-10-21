from fastapi import FastAPI

from src.routers import customers

app = FastAPI(title="Customer API")
app.include_router(customers.router)


@app.get("/health")
def health():
    return {"status": "ok"}