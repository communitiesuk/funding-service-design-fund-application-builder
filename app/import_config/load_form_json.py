import json
import os
import sys

from app.shared.helpers import human_to_kebab_case

sys.path.insert(1, ".")

from app.create_app import app  # noqa:E402
from app.db.queries.application import insert_new_form


def insert_form_as_template(form, template_name=None, filename=None):
    start_page_path = form.get("startPage")
    if "name" in form:
        form_name = form.get("name")
    else:
        # If form doesn't have a name element, use the title of the start page
        form_name = next(p for p in form["pages"] if p["path"] == start_page_path)["title"]
    if not template_name:
        template_name = filename.split(".")[0]

    new_form = insert_new_form(
        form_name=form_name,
        template_name=template_name,
        runner_publish_name=human_to_kebab_case(filename.split(".")[0]).lower(),
        form_json=form,
    )

    return new_form


def read_json_from_directory(directory_path):
    form_configs = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r") as json_file:
                form = json.load(json_file)
                form["filename"] = filename
                form_configs.append(form)
    return form_configs


def load_form_jsons(override_fund_config=None):
    db = app.extensions["sqlalchemy"]
    try:
        if not override_fund_config:
            script_dir = os.path.dirname(__file__)
            full_directory_path = os.path.join(script_dir, "files_to_import")
            form_configs = read_json_from_directory(full_directory_path)
        else:
            form_configs = override_fund_config
        for form_config in form_configs:
            insert_form_as_template(form_config["form_json"], None, form_config["filename"])
    except Exception as e:
        print(e)
        db.session.rollback()
        raise e


def load_json_from_file(data, template_name, filename):
    db = app.extensions["sqlalchemy"]
    try:
        inserted_form = insert_form_as_template(data, template_name=template_name, filename=filename)
        db.session.commit()
        return inserted_form
    except Exception as e:
        print(e)
        db.session.rollback()
        raise e


if __name__ == "__main__":
    with app.app_context():
        load_form_jsons()
