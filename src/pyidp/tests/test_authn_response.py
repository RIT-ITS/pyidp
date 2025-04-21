from saml2.client import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT


def test_no_authn_context(authn_response_factory):
    saml_resp, _ = authn_response_factory()

    assert (
        saml_resp.assertion.authn_statement[
            0
        ].authn_context.authn_context_class_ref.text
        == "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport"
    )


def test_reflect_authn_context(authn_response_factory):
    ctx_ref = "http://acme.edu/authn/password"
    saml_resp, _ = authn_response_factory(
        authn_request_args={
            "requested_authn_context": {"authn_context_class_ref": [ctx_ref]}
        }
    )
    assert (
        saml_resp.assertion.authn_statement[
            0
        ].authn_context.authn_context_class_ref.text
        == ctx_ref
    )


def test_acs_binding_post(authn_response_factory):
    saml_resp, _ = authn_response_factory(
        authn_request_args={"acs_binding": BINDING_HTTP_POST}
    )

    assert len(saml_resp.return_addrs) == 1
    assert "post" in saml_resp.return_addrs[0]


def test_acs_binding_redirect(authn_response_factory):
    saml_resp, _ = authn_response_factory(
        authn_request_args={"acs_binding": BINDING_HTTP_REDIRECT}
    )

    assert len(saml_resp.return_addrs) == 1
    assert "redirect" in saml_resp.return_addrs[0]


def test_relaystate_post(authn_response_factory):
    sent_relay_state = "relay-state"
    _, relay_state = authn_response_factory(
        authn_request_args={"relay_state": sent_relay_state}
    )
    assert sent_relay_state == relay_state


def test_relaystate_redirect(authn_response_factory):
    sent_relay_state = "relay-state"
    _, relay_state = authn_response_factory(
        authn_request_args={
            "relay_state": sent_relay_state,
            "acs_binding": BINDING_HTTP_REDIRECT,
        }
    )
    assert sent_relay_state == relay_state
