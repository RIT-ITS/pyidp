import os
import time
from typing import Literal
from urllib.parse import parse_qs, urlparse

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pyidp.app import create_app
from saml2.client import Saml2Client, BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from . import sp_conf
from saml2.config import config_factory
from pyidp.extensions import IdPApp
from saml2.pack import http_redirect_message
from bs4 import BeautifulSoup

HERE = os.path.dirname(__file__)


@pytest.fixture
def app():
    app = create_app("pyidp.tests.config.Config")
    yield app


@pytest.fixture
def app_client(app):
    return app.test_client()


@pytest.fixture
def authenticated_app_client(app_client):
    with app_client.session_transaction() as session:
        session["authenticated"] = time.time()

    return app_client


@pytest.fixture
def saml_client():
    saml_client = Saml2Client(config=config_factory("sp", sp_conf.CONFIG))
    return saml_client


type AUTHN_BINDINGS = Literal[
    "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
] | Literal["urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"]


@pytest.fixture
def authn_request_factory(saml_client: Saml2Client, app: IdPApp):
    def wrapped(
        destination: str = None,
        sign=False,
        **kwargs,
    ):
        binding = kwargs.pop("binding", BINDING_HTTP_REDIRECT)
        acs_binding = kwargs.pop("acs_binding", BINDING_HTTP_POST)
        relay_state = kwargs.pop("relay_state", None)
        if not destination:
            destination = app.idp.config.endpoint("single_sign_on_service", binding)[0]
        _, req = saml_client.create_authn_request(
            destination,
            sign=sign,
            sign_alg=app.idp.signing_algorithm,
            binding=acs_binding,
            **kwargs,
        )
        msg = http_redirect_message(
            str(req),
            location=destination,
            sign=sign,
            sigalg=app.idp.signing_algorithm,
            backend=app.idp.sec.sec_backend,
            relay_state=relay_state,
        )

        url = urlparse(dict(msg["headers"])["Location"])
        return parse_qs(url.query)

    return wrapped


@pytest.fixture
def authn_response_factory(
    authenticated_app_client, saml_client, authn_request_factory
):
    def wrapped(authn_request_args: dict = {}):
        params = authn_request_factory(
            binding=BINDING_HTTP_REDIRECT,
            **authn_request_args,
        )
        resp = authenticated_app_client.get(
            "/saml2/redirect", query_string=params, follow_redirects=True
        )
        ticket = resp.request.args["ticket"]

        profiles = authenticated_app_client.application.config["PROFILES"]
        first_profile_principal = list(profiles.keys())[0]

        resp = authenticated_app_client.post(
            "/login/profile?ticket=" + ticket,
            data={"chosenProfile": first_profile_principal},
        )

        relay_state = None
        if "location" in resp.headers:
            location = resp.headers["location"]
            destination = urlparse(location)
            query_params = parse_qs(destination.query)

            saml_resp = saml_client.parse_authn_request_response(
                query_params["SAMLResponse"][0], BINDING_HTTP_REDIRECT
            )
            try:
                relay_state = query_params["RelayState"][0]
            except:  # noqa: E722
                pass
        else:
            soup = BeautifulSoup(resp.text, features="html.parser")
            saml_resp = saml_client.parse_authn_request_response(
                soup.find_all(attrs={"name": "SAMLResponse"})[0].attrs["value"],
                BINDING_HTTP_POST,
            )
            try:
                relay_state = soup.find_all(attrs={"name": "RelayState"})[0].attrs[
                    "value"
                ]
            except:  # noqa: E722
                pass
        return saml_resp, relay_state

    return wrapped


@pytest.fixture
def keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem_private_key = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return pem_private_key.decode(), pem_public_key.decode()
