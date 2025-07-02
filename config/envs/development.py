import copy
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
        "postgresql://postgres:password@localhost:5432/fab_store",  # pragma: allowlist secret
    )
    SQLALCHEMY_RECORD_QUERIES = True
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

    # Flask-DebugToolabr
    DEBUG_TB_ENABLED = getenv("DEBUG_TB_ENABLED", "true").lower() in ("true", "1", "t", "yes", "y")
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    TALISMAN_SETTINGS = copy.deepcopy(Config.TALISMAN_SETTINGS)

    # Flask-DebugToolbar scripts
    TALISMAN_SETTINGS["content_security_policy"]["script-src"].extend(
        [
            # `var DEBUG_TOOLBAR_STATIC_PATH = '/_debug_toolbar/static/'`
            "'sha256-zWl5GfUhAzM8qz2mveQVnvu/VPnCS6QL7Niu6uLmoWU='",
        ]
    )

    # Flask-DebugToolbar styles
    TALISMAN_SETTINGS["content_security_policy"]["style-src"].extend(
        [
            "'unsafe-hashes'",
            "'sha256-0EZqoz+oBhx7gF4nvY2bSqoGyy4zLjNF+SDQXGp/ZrY='",  # `display:none;`
            "'sha256-biLFinpqYMtWHmXfkA1BPeCY0/fNt46SAZ+BBk5YUog='",  # `display: none;`
            "'sha256-fQY5fP3hSW2gDBpf5aHxpgfqCUocwOYh6zrfhhLsenY='",  # `line-height: 125%;`
            "'sha256-1NkfmhNaD94k7thbpTCKG0dKnMcxprj9kdSKzKR6K/k='",  # `width:20%`
            "'sha256-9KTa3VNMmypk8vbtqjwun0pXQtx5+yn5QoD/WlzV4qM='",  # `background: #ffffff`
            "'sha256-nkkzfdJNt7CL+ndBaKoK92Q9v/iCjSBzw//k1r9jGxU='",  # `color: #bbbbbb`
            "'sha256-vTmCV6LqM520vOLtAZ7+WhSSsaFOONqhCgj+dmpjQak='",  # `color: #333333`
            "'sha256-30uhPRk8bIWOPPNKfIRLXY96DVXF/ZHnfIZz8OBS/eg='",  # `color: #008800; font-weight: bold`
            "'sha256-SAqGh+YBD7v4qJypLeMBSlsddU4Qd67qmTMVRroKuqk='",  # `color: #0000DD; font-weight: bold`
            "'sha256-rietEaLOHfqNF3pcuzajo55dYo9i4UtLS6HN0KrBhbg='",  # `color: #007020`
            "'sha256-Ut0gFM7k9Dr9sRq/kXKsPL4P6Rh8XX0Vt+tKzrdJo7A='",  # `user-select: none;`
        ]
    )
