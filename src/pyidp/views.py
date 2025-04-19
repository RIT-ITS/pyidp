import os
from typing import Tuple
import uuid
from flask import (
    Blueprint,
    Response,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from functools import wraps
from saml2 import BINDING_HTTP_POST, BINDING_HTTP_REDIRECT
from saml2.metadata import create_metadata_string
from saml2.request import AuthnRequest
from .state import AuthnState, is_authenticated, set_authenticated
from .extensions import current_app
from saml2.samlp import authn_request_from_string, AuthnRequest as AuthnRequestP
from werkzeug.datastructures import MultiDict

blueprint = Blueprint("views", __name__, url_prefix="/")


def secret_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for("views.authenticate", **request.args.to_dict()))
        return f(*args, **kwargs)

    return decorated_function


# Example: The IdP SSO url for the binding
# receiver_address = idp.config.endpoint("single_sign_on_service", BINDING_HTTP_REDIRECT)


@blueprint.before_app_request
def before_request():
    session.permanent = True


def parse_sso_req(params: MultiDict, binding: str) -> Tuple[AuthnRequest, AuthnState]:
    encoded_request = params.get("SAMLRequest")
    if not encoded_request:
        abort(400, "Could not find SAMLRequest")

    saml_request: AuthnRequest = current_app.idp.parse_authn_request(
        params.get("SAMLRequest"),
        binding,
        params.get("RelayState"),
        params.get("Signature"),
        params.get("SigAlg"),
    )

    # Throws an error if the request is invalid
    if not saml_request:
        abort(500, "Could not parse SAMLRequest")

    binding = current_app.idp.pick_binding(
        "assertion_consumer_service", request=saml_request.message
    )
    current_app.logger.debug(
        'sender "%s" relaystate "%s" binding "%s"',
        saml_request.sender(),
        saml_request.relay_state,
        binding,
    )
    if not binding:
        abort("Could not determine valid assertion consumer service")

    state = AuthnState(
        uuid.uuid4().hex,
        str(saml_request.message),
        saml_request.sender(),
        saml_request.relay_state,
    )
    state.save()

    return saml_request, state


@blueprint.route("/saml2/post", methods=["POST"])
def sso_post():
    _, state = parse_sso_req(request.form, BINDING_HTTP_POST)
    return redirect(url_for("views.login", ticket=state.ticket))


@blueprint.route("/saml2/redirect")
def sso_redirect():
    _, state = parse_sso_req(request.args, BINDING_HTTP_REDIRECT)
    return redirect(url_for("views.login", ticket=state.ticket))


@blueprint.route("/saml2/metadata")
def metadata():
    try:
        path = os.path.dirname(os.path.abspath(__file__))
        metadata = create_metadata_string(path, current_app.idp.config)
        return Response(metadata, mimetype="text/xml")
    except Exception as ex:
        current_app.logging.error("An error occured while creating metadata: %s", ex)
        abort(500)


def load_state() -> AuthnState:
    ticket = request.args.get("ticket")
    if not ticket:
        abort(400, "Missing ticket parameter in querystring")

    state = AuthnState.load(ticket)
    if not state:
        abort(400, "Session has expired or bad ticket provided")

    return state


@blueprint.route("/authenticate", methods=["GET", "POST"])
def authenticate():
    ticket = request.args.get("ticket")
    if not ticket:
        abort(400, "Missing ticket parameter in querystring")

    token = request.form.get("token")
    error = False
    if token:
        if token.strip() == current_app.config["SECRET_KEY"].strip():
            set_authenticated()
            return redirect(url_for("views.login", ticket=ticket))
        else:
            error = True

    return render_template("authenticate.html", ticket=ticket, error=error)


@blueprint.route("/login")
@secret_required
def login():
    state = load_state()

    return render_template(
        "login.html", ticket=state.ticket, profiles=current_app.config["PROFILES"]
    )


@blueprint.route("/login/profile", methods=["POST"])
@secret_required
def choose_profile():
    state = load_state()
    message: AuthnRequestP = authn_request_from_string(state.message)

    profile_src = {}
    chosenProfileKey = request.form.get("chosenProfile")
    if chosenProfileKey:
        profile_src = {"user": chosenProfileKey} | current_app.config["PROFILES"].get(
            chosenProfileKey
        )
    else:
        for key in ["user", "mail", "givenName", "sn"]:
            profile_src[key] = request.form.get(key)
        profile_src["groups"] = request.form.getlist("groups")

    current_app.logger.debug("raw profile: %s", profile_src)
    profile = {}
    attr_conversions = current_app.config["ATTR_CONVERSIONS"]
    for key, value in profile_src.items():
        if key in attr_conversions:
            profile[attr_conversions[key]] = value
        else:
            profile[key] = value
    current_app.logger.debug("translated profile: %s", profile)
    resp_args = current_app.idp.response_args(message)

    try:
        authn_context_class_ref = (
            message.requested_authn_context.authn_context_class_ref[0].text
        )
    except AttributeError:
        authn_context_class_ref = (
            "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport"
        )

    resp = current_app.idp.create_authn_response(
        profile,
        userid=profile_src["user"],
        issuer=current_app.idp.config.entityid,
        sign_assertion=True,
        encrypt_assertion=True,
        authn={"class_ref": authn_context_class_ref},
        **resp_args
    )

    acs_binding, acs = current_app.idp.pick_binding(
        "assertion_consumer_service", request=message
    )
    saml_resp = current_app.idp.apply_binding(
        acs_binding, str(resp), acs, state.relay_state, response=True
    )

    resp = None
    if acs_binding == BINDING_HTTP_REDIRECT:
        for key, value in saml_resp["headers"]:
            if key.lower() == "location":
                resp = redirect(value)
    elif saml_resp["data"]:
        resp = Response(saml_resp["data"], headers=saml_resp["headers"])

    if not resp:
        return abort(400, "Don't know how to return response")

    return resp
