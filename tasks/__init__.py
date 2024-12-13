from invoke import task

from tasks.db_tasks import create_test_data, init_migrations, recreate_local_dbs
from tasks.export_tasks import (
    generate_assessment_config,
    generate_fund_and_round_config,
    generate_round_form_jsons,
    generate_round_html,
    publish_form_json_to_runner,
)

task.auto_dash_names = True

__all__ = [
    recreate_local_dbs,
    create_test_data,
    init_migrations,
    generate_fund_and_round_config,
    generate_assessment_config,
    generate_round_form_jsons,
    generate_round_html,
    publish_form_json_to_runner,
]
