from base64 import b64encode
from flask import Flask, request, redirect, jsonify, Response
from functools import wraps
from pathlib import Path
from hashlib import sha256
from werkzeug.routing import Rule

import bcrypt
import logging
import sys
import threading
import yaml


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


app = Flask(__name__)

# Specify the extauth route here because Flask requires manual specification of all the HTTP methods on the @app.route
# decorator which is tedious and prone to break in practice from new or custom HTTP methods being introduced.
app.url_map.add(Rule("/extauth", strict_slashes=False, endpoint="handle_authorization", defaults={"path": ""}))
app.url_map.add(Rule("/extauth/<path:path>", endpoint="handle_authorization"))

users = {}


def load_users():
    p = Path("/var/lib/ambassador/auth-basicauth/users.yaml")
    logger.debug("Loading users from file: %s", p)

    th = threading.Timer(5.0, load_users)
    th.daemon = True
    th.start()

    result = {}
    if not p.exists():
        logger.warning("Users file not found at expected path: %s", p)
    else:
        result = yaml.load(p.read_text(encoding="UTF-8"))

    global users
    users = result


load_users()


def check_auth(username, password):
    user_data = users.get(username, None)
    if user_data:
        # Passwords in the users database are stored as base64 encoded sha256 to work around the fact bcrypt only
        # supports a maximum password length of 72 characters (yes that is very long). See the below link for more
        # detail.
        #
        # see "Maximum Password Length" -> https://pypi.python.org/pypi/bcrypt/3.1.0
        prepared_password = b64encode(sha256(password.encode("UTF-8")).digest())
        return bcrypt.checkpw(prepared_password, user_data.get("hashed_password", "").encode("UTF-8"))
    else:
        return False


def unauthorized():
    return Response(status=401)


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Favicon is the little icon associated with a domain in a web browser. Browsers issue a request for the
        # resource /favicon.ico alongside any other HTTP request which pollutes the logs with lots of 404 Not Found logs
        # because usually the favicon cannot be resolved. This tells the browser to go away; there is no favicon here.
        if request.path == "/favicon.ico":
            return Response(status=403)

        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return unauthorized()

        return f(*args, **kwargs)

    return decorated


@app.errorhandler(404)
def not_found(e):
    return Response(status=404)


@app.route("/readyz", methods=["GET"])
def readyz():
    return "OK", 200


@app.route("/healthz", methods=["GET"])
def healthz():
    return "OK", 200


@app.endpoint("handle_authorization")
@requires_auth
def handle_authorization(path):
    return Response(status=200)
