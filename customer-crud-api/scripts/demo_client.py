import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
HEADERS = {"X-API-Key": os.getenv("API_KEY")}

# Unique email on each run so POST does not hit a 409
email = f"demo{int(time.time())}@example.com"

r = requests.post(
    f"{BASE_URL}/customers",
    headers=HEADERS,
    json={"name": "Demo User", "email": email, "phone": "9876543210", "city": "Chennai"},
)
print(f"POST /customers -> {r.status_code}")

r = requests.get(f"{BASE_URL}/customers?page=1&per_page=10", headers=HEADERS)
print(f"GET /customers?page=1&per_page=10 -> {r.status_code}")

r = requests.get(f"{BASE_URL}/customers/999", headers=HEADERS)
print(f"GET /customers/999 -> {r.status_code}")

r = requests.get(f"{BASE_URL}/customers")  # no X-API-Key header
print(f"No API key -> {r.status_code}")