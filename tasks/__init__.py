from invoke import task

from tasks.db_tasks import create_test_data
from tasks.db_tasks import init_migrations
from tasks.db_tasks import recreate_local_dbs
from tasks.export_tasks import generate_fund_and_round_config
from tasks.export_tasks import generate_round_form_jsons
from tasks.export_tasks import generate_round_html
from tasks.export_tasks import publish_form_json_to_runner

task.auto_dash_names = True

__all__ = [
    recreate_local_dbs,
    create_test_data,
    init_migrations,
    generate_fund_and_round_config,
    generate_round_form_jsons,
    generate_round_html,
    publish_form_json_to_runner,
]
