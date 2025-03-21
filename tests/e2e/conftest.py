import datetime
import os
import secrets
import sys
import uuid

import jwt
import pytest
from playwright.sync_api import BrowserContext, Page
from pytest import FixtureRequest
from pytest_playwright.pytest_playwright import CreateContextCallback

from config import Config
from tests.e2e.config import AWSEndToEndSecrets, EndToEndTestSecrets, LocalEndToEndSecrets
from tests.e2e.dataclass import Account, FabDomains
from tests.e2e.pages.dashboard_page import DashboardPage


@pytest.fixture
def get_e2e_params(request):
    e2e_env = request.config.getoption("e2e_env", "local")
    vault_profile = request.config.getoption("e2e_aws_vault_profile", None)
    session_token_from_env = os.getenv("AWS_SESSION_TOKEN", None)
    if not session_token_from_env and e2e_env != "local" and e2e_env != "e2e" and not vault_profile:
        sys.exit("Must supply e2e-aws-vault-profile with e2e-env")
    yield {
        "e2e_env": e2e_env,
        "e2e_aws_vault_profile": vault_profile,
    }


@pytest.fixture
def unique_token():
    yield secrets.token_urlsafe(8)


@pytest.fixture()
def domains(request: pytest.FixtureRequest, get_e2e_params) -> FabDomains:
    e2e_env = get_e2e_params["e2e_env"]
    match e2e_env:
        case "local":
            return FabDomains(
                fab_url="https://fund-application-builder.levellingup.gov.localhost:3011",
                cookie_domain=".levellingup.gov.localhost",
                environment="local",
            )
        case "e2e":
            return FabDomains(
                fab_url="http://fund-application-builder.levellingup.gov.localhost:8080",
                cookie_domain=".levellingup.gov.localhost",
                environment="e2e",
            )
        case "dev":
            return FabDomains(
                fab_url="https://fund-application-builder.access-funding.dev.communities.gov.uk",
                cookie_domain=".access-funding.dev.communities.gov.uk",
                environment="dev",
            )
        case "test":
            return FabDomains(
                fab_url="https://fund-application-builder.access-funding.test.communities.gov.uk",
                cookie_domain=".access-funding.test.communities.gov.uk",
                environment="test",
            )
        case _:
            raise ValueError(f"not configured for {e2e_env}")


@pytest.fixture
def context(
    new_context: CreateContextCallback,
    request: pytest.FixtureRequest,
    e2e_test_secrets: EndToEndTestSecrets,
    get_e2e_params,
):
    e2e_env = get_e2e_params["e2e_env"]
    http_credentials = e2e_test_secrets.HTTP_BASIC_AUTH if e2e_env in {"dev", "test"} else None

    viewport = {
        "width": 1920,
        "height": 1080,
    }
    return new_context(http_credentials=http_credentials, viewport=viewport, ignore_https_errors=True)


@pytest.fixture
def e2e_test_secrets(request: pytest.FixtureRequest, get_e2e_params) -> EndToEndTestSecrets:
    e2e_env = get_e2e_params["e2e_env"]
    e2e_aws_vault_profile = get_e2e_params["e2e_aws_vault_profile"]

    if e2e_env == "local" or e2e_env == "e2e":
        return LocalEndToEndSecrets()

    if e2e_env in {"dev", "test"}:
        return AWSEndToEndSecrets(e2e_env=e2e_env, e2e_aws_vault_profile=e2e_aws_vault_profile)

    raise ValueError(f"Unknown e2e_env: {e2e_env}.")


@pytest.fixture()
def user_auth(
    request: FixtureRequest,
    domains: FabDomains,
    context: BrowserContext,
    e2e_test_secrets: EndToEndTestSecrets,
) -> Account:
    """This fixture sets up the browser with an auth cookie so that the test user is 'logged in' correctly.

    It bypasses the standard authentication process of doing this (using Authenticator), and instead (ab)uses our
    JWT authentication model by self-signing the blob of data that authenticator provides.

    We should be careful to keep this blob of JWT data in sync with what Authenticator would actually set."""
    email_address = _generate_email_address(
        test_name=request.node.originalname,
        email_domain="communities.gov.uk",
    )
    roles_marker = request.node.get_closest_marker("user_roles")
    user_roles = roles_marker.args[0] if roles_marker else ["FSD_ADMIN"]

    now = int(datetime.datetime.timestamp(datetime.datetime.now()))
    jwt_data = {
        "accountId": str(uuid.uuid4()),
        "azureAdSubjectId": str(uuid.uuid4()),
        "email": email_address,
        "fullName": f"E2E Test User - {request.node.originalname}",
        "roles": user_roles,
        "iat": now,
        "exp": now + (15 * 60),  # 15 minutes from now
    }

    # The algorithm below must match that used by fsd-authenticator
    cookie_value = jwt.encode(jwt_data, e2e_test_secrets.JWT_SIGNING_KEY, algorithm="RS256")

    context.add_cookies(
        [
            {
                "name": Config.FSD_USER_TOKEN_COOKIE_NAME,
                "value": cookie_value,
                "domain": domains.cookie_domain,
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax",
                "exp": now + (15 * 60),
            }
        ]
    )

    return Account(email_address=email_address, roles=user_roles)


@pytest.fixture(scope="function")
def created_grant(page: Page, domains: FabDomains, user_auth):
    """
    Fixture to create a grant once per test session
    Returns the created grant details
    """
    return (
        DashboardPage(page, domains.fab_url)
        .given_user_is_on_dashboard()
        .when_click_add_a_new_grant()
        .when_fill_non_welsh_competitive_grant_details()
        .when_click_save_and_return_home()
        .and_validate_grant_success_message()
    )


def _generate_email_address(
    test_name: str,
    email_domain: str,
) -> str:
    # Help disambiguate tests running around the same time by injecting a random token into the email, so that
    # when we lookup the email it should be unique. We avoid a UUID so as to keep the emails 'short enough'.
    token = secrets.token_urlsafe(8)
    email_address = f"fsd-e2e-tests+{test_name}-{token}@{email_domain}".lower()

    return email_address
