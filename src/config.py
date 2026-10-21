import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./customers.db")
API_KEY = os.getenv("API_KEY", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")