import logging
from os import getenv

from fsd_utils import configclass

from config.envs.default import DefaultConfig as Config


@configclass
class DevelopmentConfig(Config):
    # Logging
    FSD_LOG_LEVEL = logging.DEBUG
    SECRET_KEY = "dev"  # pragma: allowlist secret

    SQLALCHEMY_DATABASE_URI = getenv(
        "DATABASE_URL",
        "postgresql://postgres:password@fab-db:5432/fab",  # pragma: allowlist secret
    )
