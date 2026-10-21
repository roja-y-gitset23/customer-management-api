import hashlib
import hmac
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()
URL = "http://127.0.0.1:8000/webhooks/customer-events"
SECRET = os.getenv("WEBHOOK_SECRET", "")


def sign(body: bytes) -> str:
    return hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()


payload = json.dumps({"event": "customer.created", "customer_id": 1}).encode()
headers = {"Content-Type": "application/json"}

# 1. Valid signature
r = requests.post(URL, data=payload, headers={**headers, "X-Signature": sign(payload)})
print("Valid signature  ->", r.status_code, r.json())

# 2. Tampered payload (signed original, sent modified body)
tampered = json.dumps({"event": "customer.created", "customer_id": 999}).encode()
r = requests.post(URL, data=tampered, headers={**headers, "X-Signature": sign(payload)})
print("Tampered payload ->", r.status_code, r.json())

# 3. Missing signature
r = requests.post(URL, data=payload, headers=headers)
print("Missing signature ->", r.status_code)