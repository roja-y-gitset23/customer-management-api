import logging
from dotenv import load_dotenv
from fastapi import FastAPI
'''
app = FastAPI(title="Customer API")
app.include_router(customers.router)
'''
load_dotenv()                                   
logging.basicConfig(level=logging.INFO)         

from src.routers import webhooks                

app = FastAPI(title="Customer Management API")
app.include_router(webhooks.router)          

@app.get("/health")
def health():
    return {"status": "ok"}