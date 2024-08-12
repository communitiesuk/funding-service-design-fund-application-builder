import pytest
from flask_migrate import upgrade
from sqlalchemy import text

from app.app import create_app
from tasks.test_data import init_unit_test_data
from tasks.test_data import insert_test_data

pytest_plugins = ["fsd_test_utils.fixtures.db_fixtures"]


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
