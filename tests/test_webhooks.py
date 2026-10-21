from tests.conftest import sign

URL = "/webhooks/customer-events"
JSON_HEADER = {"Content-Type": "application/json"}


def test_webhook_valid_signature_200(client, signed_webhook):
    body, sig = signed_webhook
    r = client.post(URL, content=body, headers={**JSON_HEADER, "X-Signature": sig})
    assert r.status_code == 200
    assert r.json() == {"status": "accepted"}


def test_webhook_tampered_payload_401(client, signed_webhook):
    body, sig = signed_webhook
    tampered = body.replace(b'"customer_id": 1', b'"customer_id": 999')
    r = client.post(URL, content=tampered, headers={**JSON_HEADER, "X-Signature": sig})
    assert r.status_code == 401


def test_webhook_wrong_signature_401(client, signed_webhook):
    body, _ = signed_webhook
    r = client.post(URL, content=body, headers={**JSON_HEADER, "X-Signature": "deadbeef"})
    assert r.status_code == 401


def test_webhook_missing_signature_401(client, signed_webhook):
    body, _ = signed_webhook
    r = client.post(URL, content=body, headers=JSON_HEADER)
    assert r.status_code == 401


def test_webhook_invalid_json_400(client):
    body = b"not json"
    r = client.post(URL, content=body, headers={**JSON_HEADER, "X-Signature": sign(body)})
    assert r.status_code == 400