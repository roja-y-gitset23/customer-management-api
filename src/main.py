import logging
from dotenv import load_dotenv
from fastapi import FastAPI
'''
app = FastAPI(title="Customer API")
app.include_router(customers.router)

load_dotenv()                                   
logging.basicConfig(level=logging.INFO)         

from src.routers import webhooks                

app = FastAPI(title="Customer Management API")
app.include_router(webhooks.router)          

@app.get("/health")
def health():
    return {"status": "ok"}'''

from fastapi import FastAPI

from src.routers import customers, webhooks

app = FastAPI(title="Customer Management API", version="1.0.0")

app.include_router(customers.router)
app.include_router(webhooks.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}