import json
import sys

import requests

from app import app

sys.path.insert(1, ".")
from invoke import task  # noqa:E402

from app.blueprints.self_serve.routes import human_to_kebab_case  # noqa:E402
from app.export_config.generate_fund_round_config import (  # noqa:E402
    generate_config_for_round,
)
from app.export_config.generate_fund_round_form_jsons import (  # noqa:E402
    generate_form_jsons_for_round,
)
from app.export_config.generate_fund_round_html import (  # noqa:E402
    generate_all_round_html,
)
from config import Config  # noqa:E402


@task
def generate_fund_and_round_config(c, roundid):
    if not roundid:
        print("Round ID is required.")
        return
    print(f"Generating fund-round configuration for round ID: {roundid}.")
    with app.app_context():
        generate_config_for_round(roundid)


@task
def generate_round_form_jsons(c, roundid):
    if not roundid:
        print("Round ID is required.")
        return
    print(f"Generating form JSON configuration for round ID: {roundid}.")
    with app.app_context():
        generate_form_jsons_for_round(roundid)


@task
def generate_round_html(c, roundid):
    if not roundid:
        print("Round ID is required.")
        return
    print(f"Generating HTML for round ID: {roundid}.")
    with app.app_context():
        generate_all_round_html(roundid)


@task
def publish_form_json_to_runner(c, filename):

    if not filename:
        print("filename is required.")
        return
    print(f"Publishing: {filename} to form runner.")

    # load json from filename
    with open(filename, "r") as file:
        form_json = file.read()
        form_dict = json.loads(form_json)
        form_dict["outputs"][0]["outputConfiguration"][
            "savePerPageUrl"
        ] = f"http://{Config.FAB_HOST}{Config.FAB_SAVE_PER_PAGE}"
        try:
            publish_response = requests.post(
                url=f"{Config.FORM_RUNNER_URL}/publish",
                json={"id": human_to_kebab_case(form_dict["name"]), "configuration": form_dict},
            )
            if not str(publish_response.status_code).startswith("2"):
                return "Error during form publish", 500
        except Exception as e:
            return f"unable to publish form: {str(e)}", 500
