import base64
import logging
from os import environ
from os import getenv
from pathlib import Path

from fsd_utils import CommonConfig
from fsd_utils import configclass


@configclass
class DefaultConfig(object):
    # Logging
    FSD_LOG_LEVEL = logging.WARNING

    FLASK_ENV = CommonConfig.FLASK_ENV
    SECRET_KEY = CommonConfig.SECRET_KEY

    FAB_HOST = getenv("FAB_HOST", "fab:8080/")
    FAB_SAVE_PER_PAGE = getenv("FAB_SAVE_PER_PAGE", "dev/save")
    FORM_RUNNER_URL = getenv("FORM_RUNNER_INTERNAL_HOST", "http://form-runner:3009")
    FORM_RUNNER_URL_REDIRECT = getenv("FORM_RUNNER_EXTERNAL_HOST", "http://localhost:3009")
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")

    TEMP_FILE_PATH = Path("/tmp")
    GENERATE_LOCAL_CONFIG = False

    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = getenv("AUTHENTICATOR_HOST", "https://authenticator.levellingup.gov.localhost:4004")

    # RSA 256 Keys
    RSA256_PUBLIC_KEY_BASE64 = getenv("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY: str = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()
