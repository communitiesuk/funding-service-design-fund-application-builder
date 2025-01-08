import json
import os
import shutil
from unittest.mock import patch

import pytest
from flask import current_app
from flask_migrate import upgrade
from sqlalchemy import text

from app.create_app import create_app
from app.import_config.load_form_json import load_form_jsons
from config import Config
from tests.seed_test_data import init_unit_test_data, insert_test_data

pytest_plugins = ["fsd_test_utils.fixtures.db_fixtures"]


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
def db_with_templates(app, _db):
    """Ensures a clean database but with templates already loaded"""
    # List of templates to load
    file_names = ["asset-information.json", "favourite-colours.json", "funding-required-cof-25.json"]
    with app.app_context():
        script_dir = os.path.dirname(__file__)
        test_data_dir = os.path.join(script_dir, "test_data")

        form_configs = []
        for file_name in file_names:
            file_path = os.path.join(test_data_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r") as json_file:
                    input_form = json.load(json_file)
                    input_form["filename"] = file_name
                    form_configs.append(input_form)
        load_form_jsons(form_configs)
    yield _db

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
    yield app


@pytest.fixture(scope="function")
def flask_test_client():
    with create_app().app_context() as app_context:
        upgrade()
        with app_context.app.test_client() as test_client:
            yield test_client


@pytest.fixture
def set_auth_cookie(flask_test_client):
    # This fixture sets the authentication cookie on every test.
    user_token_cookie_name = current_app.config.get("FSD_USER_TOKEN_COOKIE_NAME", "fsd_user_token")
    flask_test_client.set_cookie(key=user_token_cookie_name, value="dummy_jwt_token")
    yield


@pytest.fixture
def patch_validate_token_rs256_internal_user():
    # This fixture patches validate_token_rs256 for all tests automatically.
    with patch("fsd_utils.authentication.decorators.validate_token_rs256") as mock_validate_token_rs256:
        mock_validate_token_rs256.return_value = {
            "accountId": "test-account-id",
            "roles": [],
            "email": "test@communities.gov.uk",
        }
        yield mock_validate_token_rs256


@pytest.fixture
def patch_validate_token_rs256_external_user():
    # This fixture patches validate_token_rs256 for all tests automatically.
    with patch("fsd_utils.authentication.decorators.validate_token_rs256") as mock_validate_token_rs256:
        mock_validate_token_rs256.return_value = {
            "accountId": "test-account-id",
            "roles": [],
            "email": "test@gmail.com",
        }
        yield mock_validate_token_rs256
