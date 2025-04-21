from pyidp.config import Config as BaseConfig
import os

HERE = os.path.dirname(__file__)


class Config(BaseConfig):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

    @property
    def PRIVATE_KEY_FILE(self):
        return os.path.join(HERE, "tests/keys/reusable.key")

    @property
    def PUBLIC_KEY_FILE(self):
        return os.path.join(HERE, "tests/keys/reusable.crt")

    @property
    def SAML(self):
        saml = super().SAML
        saml["metadata"] = {
            "local": [os.path.join(HERE, "tests/metadata/dummy-sp.localhost.xml")]
        }
        return saml
