from geocoder.db import get_db


def test_get_db(app):
    assert get_db(app)
