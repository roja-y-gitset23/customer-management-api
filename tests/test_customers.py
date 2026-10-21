def _create(client, headers, payload):
    return client.post("/customers", json=payload, headers=headers)


# ---------------- Happy paths ----------------
def test_create_customer_201(client, auth_headers, sample_customer):
    r = _create(client, auth_headers, sample_customer)
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == sample_customer["email"]
    assert body["id"] == 1


def test_list_customers_200(client, auth_headers, sample_customer):
    _create(client, auth_headers, sample_customer)
    r = client.get("/customers", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_list_customers_pagination(client, auth_headers, sample_customer):
    for i in range(3):
        _create(client, auth_headers, {**sample_customer, "email": f"user{i}@example.com"})
    page1 = client.get("/customers?page=1&per_page=2", headers=auth_headers)
    page2 = client.get("/customers?page=2&per_page=2", headers=auth_headers)
    assert page1.status_code == 200
    assert len(page1.json()) == 2
    assert len(page2.json()) == 1


def test_get_customer_200(client, auth_headers, sample_customer):
    cid = _create(client, auth_headers, sample_customer).json()["id"]
    r = client.get(f"/customers/{cid}", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["name"] == sample_customer["name"]


def test_update_customer_200(client, auth_headers, sample_customer):
    cid = _create(client, auth_headers, sample_customer).json()["id"]
    r = client.put(f"/customers/{cid}", json={"city": "Madurai"}, headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["city"] == "Madurai"


def test_delete_customer_204(client, auth_headers, sample_customer):
    cid = _create(client, auth_headers, sample_customer).json()["id"]
    r = client.delete(f"/customers/{cid}", headers=auth_headers)
    assert r.status_code == 204
    assert client.get(f"/customers/{cid}", headers=auth_headers).status_code == 404


# ---------------- 401 ----------------
def test_create_without_api_key_401(client, sample_customer):
    assert client.post("/customers", json=sample_customer).status_code == 401


def test_wrong_api_key_401(client):
    r = client.get("/customers", headers={"X-API-Key": "wrong-key"})
    assert r.status_code == 401


def test_every_customer_endpoint_requires_key_401(client):
    assert client.get("/customers").status_code == 401
    assert client.get("/customers/1").status_code == 401
    assert client.put("/customers/1", json={"city": "X"}).status_code == 401
    assert client.delete("/customers/1").status_code == 401


# ---------------- 404 ----------------
def test_get_unknown_customer_404(client, auth_headers):
    assert client.get("/customers/999", headers=auth_headers).status_code == 404


def test_update_unknown_customer_404(client, auth_headers):
    r = client.put("/customers/999", json={"city": "X"}, headers=auth_headers)
    assert r.status_code == 404


def test_delete_unknown_customer_404(client, auth_headers):
    assert client.delete("/customers/999", headers=auth_headers).status_code == 404


# ---------------- 409 ----------------
def test_duplicate_email_on_create_409(client, auth_headers, sample_customer):
    _create(client, auth_headers, sample_customer)
    r = _create(client, auth_headers, sample_customer)
    assert r.status_code == 409


def test_duplicate_email_on_update_409(client, auth_headers, sample_customer):
    _create(client, auth_headers, sample_customer)
    other = _create(
        client, auth_headers, {**sample_customer, "email": "other@example.com"}
    ).json()
    r = client.put(
        f"/customers/{other['id']}",
        json={"email": sample_customer["email"]},
        headers=auth_headers,
    )
    assert r.status_code == 409


# ---------------- 422 ----------------
def test_invalid_email_422(client, auth_headers, sample_customer):
    r = _create(client, auth_headers, {**sample_customer, "email": "not-an-email"})
    assert r.status_code == 422


def test_missing_required_field_422(client, auth_headers):
    r = _create(client, auth_headers, {"name": "No Email"})
    assert r.status_code == 422


def test_non_numeric_id_422(client, auth_headers):
    assert client.get("/customers/abc", headers=auth_headers).status_code == 422