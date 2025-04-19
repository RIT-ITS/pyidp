import flask
from saml2.server import Server


class IdPApp(flask.Flask):
    idp: Server


current_app: IdPApp = flask.current_app
