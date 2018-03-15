import pytest


from ambassador_auth import app as ambassador_auth_app


@pytest.fixture
def app():
    app_under_test = ambassador_auth_app.app
    return app_under_test
