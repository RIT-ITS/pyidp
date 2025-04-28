import os

import yaml

from cachelib import FileSystemCache
from saml2 import BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from saml2.saml import NAMEID_FORMAT_PERSISTENT

HERE = os.path.dirname(__file__)


def _(key: str, default: str | None = None, must_exist=False) -> str | None:
    val = os.environ.get(key, default)
    if not val and must_exist:
        raise Exception(f"Environment variable {key} must be set")

    return val


class Config:
    SESSION_TYPE = "cachelib"
    SESSION_SERIALIZATION_FOFRMAT = "json"
    SESSION_CACHELIB = FileSystemCache(threshold=0, cache_dir="/tmp/flask-sessions")

    @property
    def BASE_URL(self):
        return _("BASE_URL", "https://pyidp.localtest.me")

    @property
    def PRIVATE_KEY_FILE(self):
        return _("PRIVATE_KEY_FILE", "/etc/pyidp/idp.key")

    @property
    def PUBLIC_KEY_FILE(self):
        return _("PUBLIC_KEY_FILE", "/etc/pyidp/idp.crt")

    @property
    def SECRET_KEY(self):
        return _("SECRET_KEY", must_exist=True)

    @property
    def ATTR_CONVERSIONS(self):
        return {"user": "uid"}

    @property
    def PROFILES(self):
        LOCAL_PROFILES_FILE = _("PROFILES_FILE", "/etc/pyidp/profiles.yaml")
        if os.path.exists(LOCAL_PROFILES_FILE):
            return yaml.safe_load(open(LOCAL_PROFILES_FILE))
        else:
            return {
                "admin@acme.edu": {
                    "user": "admin@acme.edu",
                    "mail": "admin@mail.acme.edu",
                    "givenName": "Admin",
                    "sn": "User",
                    "groups": ["admin", "Domain Users"],
                },
                "staff@acme.edu": {
                    "user": "staff@acme.edu",
                    "mail": "staff@mail.acme.edu",
                    "givenName": "Staff",
                    "sn": "User",
                    "groups": [
                        "staff",
                        "its_staff",
                        "its_staff_fte",
                        "Domain Users",
                    ],
                },
                "faculty@acme.edu": {
                    "user": "faculty@acme.edu",
                    "mail": "faculty@mail.acme.edu",
                    "givenName": "Faculty",
                    "sn": "User",
                    "groups": ["faculty", "faculty_fte", "Domain Users"],
                },
                "student@acme.edu": {
                    "user": "student@acme.edu",
                    "mail": "student@mail.acme.edu",
                    "givenName": "Student",
                    "sn": "User",
                    "groups": ["student", "Domain Users"],
                },
                "transient@acme.edu": {"user": "transient@acme.edu"},
            }

    @property
    def SAML(self):
        return {
            "entityid": _("IDP_ENTITY_ID", f"{self.BASE_URL}/saml2"),
            "service": {
                "idp": {
                    "sign_assertion": True,
                    "sign_response": True,
                    "want_authn_requests_signed": _("WANT_AUTHN_REQUESTS_SIGNED", "0")
                    == "1",
                    "encrypt_assertion": True,
                    "endpoints": {
                        "single_sign_on_service": [
                            (f"{self.BASE_URL}/saml2/redirect", BINDING_HTTP_REDIRECT),
                            (f"{self.BASE_URL}/saml2/post", BINDING_HTTP_POST),
                        ]
                    },
                    "name_id_format": [NAMEID_FORMAT_PERSISTENT],
                },
            },
            "metadata": {
                "local": ["/etc/pyidp/sp.xml"],
            },
            "attribute_map_dir": os.path.join(HERE, "attributemaps"),
            "key_file": self.PRIVATE_KEY_FILE,
            "cert_file": self.PUBLIC_KEY_FILE,
            "encryption_keypairs": [
                {"key_file": self.PRIVATE_KEY_FILE, "cert_file": self.PUBLIC_KEY_FILE},
            ],
            "xmlsec_binary": "/usr/bin/xmlsec1",
        }
