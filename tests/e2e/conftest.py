import os
import secrets
import sys

import pytest
from pytest_playwright import CreateContextCallback

from tests.e2e.config import AWSEndToEndSecrets, EndToEndTestSecrets, LocalEndToEndSecrets


@pytest.fixture
def get_e2e_params(request):
    e2e_env = request.config.getoption("e2e_env", "local")
    vault_profile = request.config.getoption("e2e_aws_vault_profile", None)
    session_token_from_env = os.getenv("AWS_SESSION_TOKEN", None)
    if not session_token_from_env and e2e_env != "local" and not vault_profile:
        sys.exit("Must supply e2e-aws-vault-profile with e2e-env")
    yield {
        "e2e_env": e2e_env,
        "e2e_aws_vault_profile": vault_profile,
    }


@pytest.fixture
def unique_token():
    yield secrets.token_urlsafe(8)


@pytest.fixture()
def domains(request: pytest.FixtureRequest, get_e2e_params) -> str:
    e2e_env = get_e2e_params["e2e_env"]
    match e2e_env:
        case "local":
            return "https://fund-application-builder.levellingup.gov.localhost:3011"
        case "dev":
            return "https://fund-application-builder.dev.access-funding.test.levellingup.gov.uk"
        case "test":
            return "https://fund-application-builder.test.access-funding.test.levellingup.gov.uk"
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
    return new_context(http_credentials=http_credentials)


@pytest.fixture
def e2e_test_secrets(request: pytest.FixtureRequest, get_e2e_params) -> EndToEndTestSecrets:
    e2e_env = get_e2e_params["e2e_env"]
    e2e_aws_vault_profile = get_e2e_params["e2e_aws_vault_profile"]

    if e2e_env == "local":
        return LocalEndToEndSecrets()

    if e2e_env in {"dev", "test"}:
        return AWSEndToEndSecrets(e2e_env=e2e_env, e2e_aws_vault_profile=e2e_aws_vault_profile)

    raise ValueError(f"Unknown e2e_env: {e2e_env}.")
