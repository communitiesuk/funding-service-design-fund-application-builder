import os
import sys
from os import getenv

from flask_migrate import upgrade
from invoke import task  # noqa:E402

from app import app
from app.import_config.load_form_json import load_form_jsons

sys.path.insert(1, ".")
os.environ.update({"FLASK_ENV": "tasks"})

from .test_data import init_salmon_fishing_fund  # noqa:E402
from .test_data import insert_test_data  # noqa:E402


@task
def recreate_local_dbs(c):
    """Create a clean database for development.

    Unit testing makes a seperate db.

    """

    from sqlalchemy_utils.functions import create_database
    from sqlalchemy_utils.functions import database_exists
    from sqlalchemy_utils.functions import drop_database

    uris = [
        getenv(
            "DATABASE_URL",
            "postgresql://postgres:password@fab-db:5432/fab",  # pragma: allowlist secret
        ),
        getenv(
            "DATABASE_URL_UNIT_TEST",
            "postgresql://postgres:password@fab-db:5432/fab_unit_test",  # pragma: allowlist secret
        ),
    ]
    with app.app_context():
        for db_uri in uris:
            if database_exists(db_uri):
                print("Existing database found!\n")
                drop_database(db_uri)
                print("Existing database dropped!\n")
            else:
                print(
                    f"{db_uri} not found...",
                )
            create_database(db_uri)
            print(
                f"{db_uri} db created...",
            )
            upgrade()


@task
def create_test_data(c):
    """Inserts some initial test data"""
    from sqlalchemy import text

    with app.app_context():
        db = app.extensions["sqlalchemy"]
        db.session.execute(
            text(
                "TRUNCATE TABLE fund, round, section,form, page, component, criteria, "
                "subcriteria, theme, lizt, organisation CASCADE;"
            )
        )
        db.session.commit()
        insert_test_data(db=db, test_data=init_salmon_fishing_fund())
        load_form_jsons()


@task
def init_migrations(c):
    """Deletes the migrations/versions folder and recreates migrations from scratch"""

    import os
    import shutil

    from flask_migrate import migrate

    with app.app_context():
        try:
            versions_path = "./app/db/migrations/versions/"
            if os.path.exists(versions_path):
                shutil.rmtree(versions_path)
                os.mkdir(versions_path)
        except Exception as e:
            print("Could not delete folder " + str(e))
        migrate()
