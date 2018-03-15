# Copyright 2018 Datawire Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ambassador_auth import app
from base64 import b64encode
from hashlib import sha256
from pathlib import Path

import yaml


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


def test_auth_succeeds_with_valid_credentials(client):
    app.users = {
        "admin": {
            "hashed_password": create_hashed_password("IAmTheWalrus")
        }
    }

    headers = {"Authorization": create_basic_auth("admin", "IAmTheWalrus")}

    r = client.get("/extauth", headers=headers)
    assert 200 == r.status_code


def test_load_credentials_from_file(tmpdir):
    p = Path(tmpdir)

    users_file_under_test = p / "users.yaml"
    users_file_under_test.touch()

    app.users_file = users_file_under_test
    credentials = {
        "admin": {"hashed_password": create_hashed_password("IAmTheWalrus")},
        "user1": {"hashed_password": create_hashed_password("CooCooKaChoo")}
    }

    users_file_under_test.write_text(yaml.dump(credentials))

    app.load_users()
    assert "admin" in app.users
    assert "user1" in app.users


def create_basic_auth(username, password):
    return "Basic " + b64encode((username + ":" + password).encode("utf-8")).decode("utf-8")


def create_hashed_password(password):
    import bcrypt

    prepared_password = b64encode(sha256(password.encode("UTF-8")).digest())
    return bcrypt.hashpw(prepared_password, bcrypt.gensalt()).decode("utf-8")
