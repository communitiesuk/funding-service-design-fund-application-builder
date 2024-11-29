import logging
from os import getenv
from pathlib import Path

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
    TEMP_FILE_PATH = Path("app") / "export_config" / "output"

    GENERATE_LOCAL_CONFIG = True

    DEBUG_USER_ON = True
    DEBUG_USER = {
        "full_name": "Development User",
        "email": "dev@communities.gov.uk",
        "roles": [],
        "highest_role_map": {},
    }
    DEBUG_USER_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"
