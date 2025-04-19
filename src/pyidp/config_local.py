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
