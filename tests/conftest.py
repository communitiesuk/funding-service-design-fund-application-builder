import pytest

pytest_plugins = ["fsd_test_utils.fixtures.db_fixtures"]


def pytest_addoption(parser):
    parser.addoption(
        "--e2e", action="store_true", default=False, help="Run end-to-end tests"
    )
    parser.addoption(
        "--e2e-aws-vault-profile",
        action="store",
        help="the aws-vault profile matching the env set in --e2e-env (for `dev` or `test` only)",
    )
    parser.addoption(
        "--e2e-env",
        action="store",
        default="local",
        help="choose the environment that e2e tests will target",
        choices=("local", "dev", "test"),
    )


def pytest_collection_modifyitems(config, items):
    skip_e2e = pytest.mark.skip(reason="only running unit tests")
    skip_non_e2e = pytest.mark.skip(reason="only running e2e tests")

    e2e_run = config.getoption("--e2e")
    if e2e_run:
        for item in items:
            if "e2e" not in item.keywords:
                item.add_marker(skip_non_e2e)
    else:
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)
