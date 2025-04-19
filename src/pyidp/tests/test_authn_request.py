from flask.testing import FlaskClient
from pyidp.extensions import IdPApp
import pytest
from saml2 import BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.response import IncorrectlySigned
from saml2.s_utils import OtherError, UnravelError


def test_redirect_successful(app_client: FlaskClient, authn_request_factory):
    params = authn_request_factory(binding=BINDING_HTTP_REDIRECT)
    resp = app_client.get("/saml2/redirect", query_string=params)

    assert resp.status_code == 302
    assert "ticket" in resp.headers["location"]


def test_redirect_wrong_binding(app_client: FlaskClient, authn_request_factory):
    with pytest.raises(OtherError):
        params = authn_request_factory(binding=BINDING_HTTP_POST)
        app_client.get("/saml2/redirect", query_string=params)


def test_redirect_undecodable(app_client: FlaskClient):
    with pytest.raises(UnravelError):
        app_client.get("/saml2/redirect", query_string={"SAMLRequest": "cantunravel"})


def test_signed_redirect_request(app_client: FlaskClient, authn_request_factory):
    params = authn_request_factory(binding=BINDING_HTTP_REDIRECT, sign=True)
    assert "SigAlg" in params
    assert "Signature" in params
    resp = app_client.get("/saml2/redirect", query_string=params)

    assert resp.status_code == 302
    assert "ticket" in resp.headers["location"]


def test_incorrectly_signed_redirect_request(
    app: IdPApp,
    app_client: FlaskClient,
    saml_client: Saml2Client,
    authn_request_factory,
):
    with pytest.raises(IncorrectlySigned):
        # Valid entity id but the request will be signed with the initial settings, so
        # it will fail.
        saml_client.config.entityid = "https://acme2.edu/saml2/"
        params = authn_request_factory(binding=BINDING_HTTP_REDIRECT, sign=True)
        app_client.get("/saml2/redirect", query_string=params)


def test_post_successful(app_client: FlaskClient, authn_request_factory):
    params = authn_request_factory(binding=BINDING_HTTP_POST)
    resp = app_client.post("/saml2/post", data=params)

    assert resp.status_code == 302
    assert "ticket" in resp.headers["location"]


def test_post_wrong_binding(app_client: FlaskClient, authn_request_factory):
    with pytest.raises(OtherError):
        params = authn_request_factory(binding=BINDING_HTTP_REDIRECT)
        app_client.post("/saml2/post", data=params)


def test_post_undecodable(app_client: FlaskClient):
    with pytest.raises(UnravelError):
        app_client.post("/saml2/post", data={"SAMLRequest": "cantunravel"})


def test_signed_post_request(app_client: FlaskClient, authn_request_factory):
    params = authn_request_factory(binding=BINDING_HTTP_POST, sign=True)
    assert "SigAlg" in params
    assert "Signature" in params
    resp = app_client.post("/saml2/post", data=params)

    assert resp.status_code == 302
    assert "ticket" in resp.headers["location"]


def test_incorrectly_signed_post_request(
    app: IdPApp,
    app_client: FlaskClient,
    saml_client: Saml2Client,
    authn_request_factory,
):
    with pytest.raises(IncorrectlySigned):
        # Valid entity id but the request will be signed with the initial settings, so
        # it will fail.
        saml_client.config.entityid = "https://acme2.edu/saml2/"
        params = authn_request_factory(binding=BINDING_HTTP_POST, sign=True)
        app_client.post("/saml2/post", data=params)
