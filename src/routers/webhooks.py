'''
import hashlib
import hmac
import json
import logging
import os

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

router = APIRouter(tags=["webhooks"])
logger = logging.getLogger("webhooks")


def process_event(raw_body: bytes) -> None:
    """Runs in the background after the 200 response is sent."""
    try:
        event = json.loads(raw_body)
    except json.JSONDecodeError:
        event = {"raw": raw_body.decode(errors="replace")}
    logger.info("Processed customer event: %s", event)


@router.post("/webhooks/customer-events")
async def customer_events(
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: str | None = Header(default=None),
):
    raw_body = await request.body()  # raw bytes, exactly as sent

    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    secret = os.getenv("WEBHOOK_SECRET", "")
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    background_tasks.add_task(process_event, raw_body)
    return {"status": "accepted"}
'''
import hashlib
import hmac
import json
import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request

from src import config

router = APIRouter(tags=["webhooks"])
logger = logging.getLogger("webhooks")


def process_event(payload: dict):
    logger.info("Processing customer event: %s", payload)


@router.post("/webhooks/customer-events")
async def customer_events(
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: Optional[str] = Header(default=None),
):
    body = await request.body()

    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    expected = hmac.new(config.WEBHOOK_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected.encode(), x_signature.encode()):
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(body)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    background_tasks.add_task(process_event, payload)
    return {"status": "accepted"}