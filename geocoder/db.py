from quart_db import QuartDB


def get_db(app):
    # QuartDB will place a database connection on the g global object.
    return QuartDB(app, url=app.config["DATABASE_URL"].replace("postgis", "postgresql"))


def init_db(app):
    get_db(app)
