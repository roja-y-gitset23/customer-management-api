import hmac
from typing import Optional

from fastapi import Header, HTTPException

from src import config


def verify_api_key(x_api_key: Optional[str] = Header(default=None)):
    if (
        not x_api_key
        or not config.API_KEY
        or not hmac.compare_digest(x_api_key.encode(), config.API_KEY.encode())
    ):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")