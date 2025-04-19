from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from saml2 import BINDING_HTTP_REDIRECT
from urllib.parse import urlparse, parse_qs
from saml2.client import Saml2Client


def _get_ticket(app_client: FlaskClient, authn_request_factory):
    params = authn_request_factory(
        binding=BINDING_HTTP_REDIRECT, acs_binding=BINDING_HTTP_REDIRECT
    )
    resp = app_client.get("/saml2/redirect", query_string=params, follow_redirects=True)
    return resp.request.args["ticket"]


def _assert_profile_in_response(
    resp: TestResponse, saml_client: Saml2Client, app_client: FlaskClient, profile: dict
):
    assert resp.status_code == 302
    location = resp.headers["location"]
    destination = urlparse(location)
    query_params = parse_qs(destination.query)

    saml_resp = saml_client.parse_authn_request_response(
        query_params["SAMLResponse"][0], BINDING_HTTP_REDIRECT
    )

    rev_attr_conversions = {
        v: k for k, v in app_client.application.config["ATTR_CONVERSIONS"].items()
    }

    assert len(saml_resp.ava) > 0

    for key, value in saml_resp.ava.items():
        if key in rev_attr_conversions:
            key = rev_attr_conversions[key]
        assert profile[key] == value or [profile[key]] == value


def test_choose_profile(
    app_client: FlaskClient, authn_request_factory, saml_client: Saml2Client
):
    ticket = _get_ticket(app_client, authn_request_factory)

    profiles = app_client.application.config["PROFILES"]
    first_profile_principal = list(profiles.keys())[0]
    first_profile = profiles[first_profile_principal]

    resp = app_client.post(
        "/login/profile?ticket=" + ticket,
        data={"chosenProfile": first_profile_principal},
    )

    _assert_profile_in_response(
        resp, saml_client, app_client, {"user": first_profile_principal} | first_profile
    )


def test_provide_custom_profile(
    app_client: FlaskClient, authn_request_factory, saml_client: Saml2Client
):
    ticket = _get_ticket(app_client, authn_request_factory)

    profile = {
        "user": "testusr@acme.edu",
        "mail": "testusr@mail.acme.edu",
        "givenName": "Test",
        "sn": "User",
        "groups": ["tester", "Domain Users"],
    }

    resp = app_client.post(
        "/login/profile?ticket=" + ticket,
        data=profile,
    )

    _assert_profile_in_response(resp, saml_client, app_client, profile)


def test_provide_custom_profile_no_groups(
    app_client: FlaskClient, authn_request_factory, saml_client: Saml2Client
):
    ticket = _get_ticket(app_client, authn_request_factory)

    profile = {
        "user": "testusr@acme.edu",
        "mail": "testusr@mail.acme.edu",
        "givenName": "Test",
        "sn": "User",
    }

    resp = app_client.post(
        "/login/profile?ticket=" + ticket,
        data=profile,
    )

    _assert_profile_in_response(resp, saml_client, app_client, {"groups": []} | profile)
