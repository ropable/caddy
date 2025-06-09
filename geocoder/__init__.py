import os

from quart import Quart

# from quart_db import QuartDB

dot_env = os.path.join(os.getcwd(), ".env")
if os.path.exists(dot_env):
    from dotenv import load_dotenv

    load_dotenv()


def create_app(test_config=None):
    """The application factory, used to generate the Quart instance."""
    app = Quart(__name__)
    app.config.from_prefixed_env()  # Loads env vars prefixed with QUART_

    if test_config:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # Initialise the database.
    from geocoder import db

    db.init_db(app)

    # Register views.
    from geocoder import views

    app.register_blueprint(views.bp)
    app.add_url_rule("/", endpoint="index")
    app.add_url_rule("/api/<int:object_id>", endpoint="detail")
    app.add_url_rule("/api/geocode", endpoint="geocode")
    app.add_url_rule("/livez", endpoint="liveness")
    app.add_url_rule("/readyz", endpoint="readiness")
    app.add_url_rule("/favicon.ico", endpoint="favicon")

    return app


# Instantiate the application object for the purposes of deployment.
app = create_app()
