import base64
import logging
from os import environ, getenv
from pathlib import Path

from fsd_utils import CommonConfig, configclass


@configclass
class DefaultConfig(object):
    # Logging
    FSD_LOG_LEVEL = logging.WARNING

    FLASK_ENV = CommonConfig.FLASK_ENV
    SECRET_KEY = CommonConfig.SECRET_KEY

    FUND_APPLICATION_BUILDER_HOST = getenv(
        "FUND_APPLICATION_BUILDER_HOST", "https://fund-application-builder.levellingup.gov.localhost:3011"
    )
    FAB_SAVE_PER_PAGE = getenv("FAB_SAVE_PER_PAGE", "dev/save")
    FORM_RUNNER_URL = getenv("FORM_RUNNER_INTERNAL_HOST", "http://form-runner:3009")
    FORM_RUNNER_URL_REDIRECT = getenv("FORM_RUNNER_EXTERNAL_HOST", "http://localhost:3009")
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")

    TEMP_FILE_PATH = Path("/tmp")
    GENERATE_LOCAL_CONFIG = False

    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = getenv("AUTHENTICATOR_HOST", "https://authenticator.levellingup.gov.localhost:4004")
    LOGOUT_URL_OVERRIDE = f"{AUTHENTICATOR_HOST}/sessions/sign-out?return_app=fund-application-builder&return_path=/"  # noqa: E501
    # RSA 256 Keys
    RSA256_PUBLIC_KEY_BASE64 = getenv("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY: str = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()

    # Content Security Policy
    SECURE_CSP = {
        "default-src": "'self'",
        "script-src": ["'self'"],  # Needed to enable nonce
    }

    # Talisman Config
    FSD_REFERRER_POLICY = "strict-origin-when-cross-origin"
    FSD_USER_TOKEN_COOKIE_SAMESITE = "Lax"
    FSD_SESSION_COOKIE_SAMESITE = "Lax"
    FSD_PERMISSIONS_POLICY = {"interest-cohort": "()"}
    FSD_DOCUMENT_POLICY = {}
    FSD_FEATURE_POLICY = {
        "microphone": "'none'",
        "camera": "'none'",
        "geolocation": "'none'",
    }

    DENY = "DENY"
    SAMEORIGIN = "SAMEORIGIN"
    ALLOW_FROM = "ALLOW-FROM"
    ONE_YEAR_IN_SECS = 31556926
    FORCE_HTTPS = False

    TALISMAN_SETTINGS = {
        "feature_policy": FSD_FEATURE_POLICY,
        "permissions_policy": FSD_PERMISSIONS_POLICY,
        "document_policy": FSD_DOCUMENT_POLICY,
        "force_https": FORCE_HTTPS,
        "force_https_permanent": False,
        "force_file_save": False,
        "frame_options": "SAMEORIGIN",
        "frame_options_allow_from": None,
        "strict_transport_security": True,
        "strict_transport_security_preload": True,
        "strict_transport_security_max_age": ONE_YEAR_IN_SECS,
        "strict_transport_security_include_subdomains": True,
        "content_security_policy": SECURE_CSP,
        "content_security_policy_report_uri": None,
        "content_security_policy_report_only": False,
        "referrer_policy": FSD_REFERRER_POLICY,
        "session_cookie_secure": True,
        "session_cookie_http_only": True,
        "session_cookie_samesite": FSD_SESSION_COOKIE_SAMESITE,
        "x_content_type_options": True,
        "x_xss_protection": True,
        "content_security_policy_nonce_in": ["script-src"],
    }
