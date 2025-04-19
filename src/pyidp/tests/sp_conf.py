import os
from saml2 import BINDING_HTTP_REDIRECT, BINDING_HTTP_POST

HERE = os.path.dirname(__file__)
BASE_URL = "https://acme.edu/"
# your generated entity id
SP_ENTITY_ID = f"{BASE_URL}saml2/"
# path to a base64 encoded private key (PEM) for the SP
SP_KEY_PATH = os.path.join(HERE, "keys/reusable.key")
# path to a base64 encoded certificate (PEM) for the SP
SP_CERT_PATH = os.path.join(HERE, "keys/reusable.crt")
# End SP Section

# IdP Section
# single-sign-on url for your IdP
IDP_SSO_URL = "https://pyidp.localtest.me/saml2/redirect"
# Path to the metadata downloaded from your IdP.
IDP_METADATA_PATH = os.path.join(HERE, "metadata/dummy-idp.localhost.xml")
# End IdP Section

CONFIG = {
    "entityid": SP_ENTITY_ID,
    # Name of your service in metadata
    "name": "Python Test Client",
    "service": {
        "sp": {
            # Allow a user to initiate login from the IdP
            "allow_unsolicited": True,
            "authn_requests_signed": False,
            "endpoints": {
                # Callback service that parses SAML attributes
                "assertion_consumer_service": [
                    (f"{BASE_URL}saml2/acs-redirect", BINDING_HTTP_REDIRECT),
                    (f"{BASE_URL}saml2/acs-post", BINDING_HTTP_POST),
                ],
                # Service the app requests when logging in
                "single_sign_on_service": [IDP_SSO_URL],
            },
        },
    },
    "metadata": {"local": [IDP_METADATA_PATH]},
    "allow_unknown_attributes": True,
    "metadata_key_usage": "both",
    # Keypair used to sign xml payloads
    "key_file": SP_KEY_PATH,
    "cert_file": SP_CERT_PATH,
    # Keypair used to encrypt xml payloads
    "encryption_keypairs": [
        {
            "key_file": SP_KEY_PATH,
            "cert_file": SP_CERT_PATH,
        },
    ],
    # Path the xmlsec binary, this will likely change depending on your
    # base image
    "xmlsec_binary": "/usr/bin/xmlsec1",
    "delete_tmpfiles": True,
    "attribute_map_dir": os.path.join(HERE, "attributemaps"),
}
