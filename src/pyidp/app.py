from datetime import timedelta
from saml2.config import config_factory
from saml2.server import Server
from werkzeug.utils import import_string
from .config import Config
from .extensions import IdPApp
from .logging import configure as configure_logging
from .views import blueprint
from flask_session import Session


def create_app(config_object="pyidp.config.Config"):
    app = IdPApp(__name__)
    config: Config = import_string(config_object)()

    app.secret_key = config.SECRET_KEY
    app.permanent_session_lifetime = timedelta(days=1)

    configure_logging(config)
    app.config.from_object(config)

    Session(app)
    app.register_blueprint(blueprint)
    app.idp = Server(config=config_factory("idp", config.SAML))

    return app
