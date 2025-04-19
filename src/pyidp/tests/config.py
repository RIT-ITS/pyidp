from pyidp.config import Config as BaseConfig
import os

HERE = os.path.dirname(__file__)


class Config(BaseConfig):
    TESTING = True

    @property
    def PRIVATE_KEY_FILE(self):
        return os.path.join(HERE, "keys/reusable.key")

    @property
    def PUBLIC_KEY_FILE(self):
        return os.path.join(HERE, "keys/reusable.crt")

    @property
    def ATTR_CONVERSIONS(self):
        return {"user": "uid", "groups": "testGroups"}

    @property
    def SAML(self):
        saml = super().SAML
        saml["metadata"] = {
            "local": [os.path.join(HERE, "metadata/dummy-sp.localhost.xml")]
        }
        return saml
