import os

import pytest

from geocoder import create_app

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture(name="app")
def app():
    database_url = os.getenv("QUART_DATABASE_URL", "").replace("postgis", "postgresql")
    app = create_app(
        {
            "TESTING": True,
            "DEBUG": 1,
            "DATABASE_URL": database_url,
        }
    )

    return app


@pytest.fixture(name="client")
def client(app):
    return app.test_client()
