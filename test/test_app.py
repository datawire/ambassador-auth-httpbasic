from ambassador_auth import app

from base64 import b64encode
from hashlib import sha256


def test_healthz(client):
    r = client.get("/healthz")
    assert 200 == r.status_code


def test_readyz(client):
    r = client.get("/healthz")
    assert 200 == r.status_code


def test_auth_fails_with_invalid_credentials(client):
    headers = {"Authorization": create_basic_auth("foo", "bar")}

    r = client.get("/extauth", headers=headers)
    assert 401 == r.status_code


def test_auth_succeeds_with_invalid_credentials(client):
    app.users = {
        "admin": {
            "hashed_password": create_hashed_password("IAmTheWalrus")
        }
    }

    headers = {"Authorization": create_basic_auth("admin", "IAmTheWalrus")}

    r = client.get("/extauth", headers=headers)
    assert 200 == r.status_code


def create_basic_auth(username, password):
    return "Basic " + b64encode((username + ":" + password).encode("utf-8")).decode("utf-8")


def create_hashed_password(password):
    import bcrypt

    prepared_password = b64encode(sha256(password.encode("UTF-8")).digest())
    return bcrypt.hashpw(prepared_password, bcrypt.gensalt()).decode("utf-8")
