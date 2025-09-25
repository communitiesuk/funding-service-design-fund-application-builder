import json
import os
import shutil
from unittest.mock import patch

import pytest
from flask import current_app
from flask_migrate import upgrade
from sqlalchemy import text

from app.create_app import create_app
from config import Config
from tests.seed_test_data import fund_without_assessment, init_unit_test_data, insert_test_data

pytest_plugins = ["fsd_test_utils.fixtures.db_fixtures"]


def read_json_from_directory(directory_path):
    form_configs = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r") as json_file:
                form_config = {
                    "filename": filename,
                    "form_json": json.load(json_file),
                }
                form_configs.append(form_config)
    return form_configs


@pytest.fixture(scope="session")
def temp_output_dir():
    temp_dir = Config.TEMP_FILE_PATH
    yield temp_dir
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture(scope="function")
def seed_dynamic_data(request, app, clear_test_data, _db, enable_preserve_test_data):
    marker = request.node.get_closest_marker("seed_config")

    if marker is None:
        fab_seed_data = init_unit_test_data()
    else:
        fab_seed_data = marker.args[0]
    insert_test_data(db=_db, test_data=fab_seed_data)
    yield fab_seed_data
    # cleanup data after test
    # rollback incase of any errors during test session
    _db.session.rollback()
    # disable foreign key checks
    _db.session.execute(text("SET session_replication_role = replica"))
    # delete all data from tables
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    # reset foreign key checks
    _db.session.execute(text("SET session_replication_role = DEFAULT"))
    _db.session.commit()


@pytest.fixture(scope="function")
def seed_fund_without_assessment(request, app, clear_test_data, _db, enable_preserve_test_data):
    marker = request.node.get_closest_marker("seed_config")

    if marker is None:
        fab_seed_data = fund_without_assessment()
    else:
        fab_seed_data = marker.args[0]
    insert_test_data(db=_db, test_data=fab_seed_data)
    yield fab_seed_data
    # cleanup data after test
    # rollback incase of any errors during test session
    _db.session.rollback()
    # disable foreign key checks
    _db.session.execute(text("SET session_replication_role = replica"))
    # delete all data from tables
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    # reset foreign key checks
    _db.session.execute(text("SET session_replication_role = DEFAULT"))
    _db.session.commit()


@pytest.fixture(scope="function")
def clean_db(app, _db):
    """Ensures a clean database before each test runs"""
    with app.app_context():
        # Rollback any existing transactions
        _db.session.rollback()
        # Disable foreign key constraints
        _db.session.execute(text("SET session_replication_role = replica"))
        # Clear all tables
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        # Re-enable foreign key constraints
        _db.session.execute(text("SET session_replication_role = DEFAULT"))
        _db.session.commit()
    yield _db


@pytest.fixture(scope="session")
def app():
    app = create_app()
    # this will enable the usage of url_for but use the app context in the test
    app.config["TESTING"] = True
    app.config["SERVER_NAME"] = "localhost"
    with app.app_context():
        yield app


@pytest.fixture(scope="function")
def flask_test_client(app):
    with app.app_context():
        upgrade()
        with app.test_client() as test_client:
            with test_client.session_transaction() as session:
                session["visited_pages"] = []  # Initialize the session for the test
            yield test_client


@pytest.fixture
def set_auth_cookie(flask_test_client):
    # This fixture sets the authentication cookie on every test.
    user_token_cookie_name = current_app.config.get("FSD_USER_TOKEN_COOKIE_NAME", "fsd_user_token")
    flask_test_client.set_cookie(key=user_token_cookie_name, value="dummy_jwt_token")
    yield


@pytest.fixture
def patch_validate_token_rs256_allowed_domain_user():
    # This fixture patches validate_token_rs256 for users with allowed domains
    with patch("fsd_utils.authentication.decorators.validate_token_rs256") as mock_validate_token_rs256:
        mock_validate_token_rs256.return_value = {
            "accountId": "test-account-id",
            "roles": ["FSD_ADMIN"],
            "email": "user@communities.gov.uk",  # An allowed domain by default
        }
        yield mock_validate_token_rs256


@pytest.fixture
def patch_validate_token_rs256_disallowed_domain_user():
    # This fixture patches validate_token_rs256 for users with disallowed domains
    with patch("fsd_utils.authentication.decorators.validate_token_rs256") as mock_validate_token_rs256:
        mock_validate_token_rs256.return_value = {
            "accountId": "test-account-id",
            "roles": ["FSD_ADMIN"],
            "email": "user@example.com",  # A domain not in the allowed list
        }
        yield mock_validate_token_rs256


def pytest_addoption(parser):
    parser.addoption("--e2e", action="store_true", default=False, help="Run end-to-end tests")
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
        choices=("local", "dev", "test", "e2e"),
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
