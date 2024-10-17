# pip install pandas openpyxl

import json
import os
import sys
from uuid import UUID

from app.db.queries.application import get_list_by_name
from app.db.queries.application import insert_list
from app.export_config.generate_form import human_to_kebab_case

sys.path.insert(1, ".")
from dataclasses import asdict  # noqa:E402

from app.create_app import app  # noqa:E402
from app.db import db  # noqa:E402
from app.db.models import Component  # noqa:E402
from app.db.models import ComponentType  # noqa:E402
from app.db.models import Form  # noqa:E402
from app.db.models import Page  # noqa:E402
from app.shared.data_classes import Condition  # noqa:E402
from app.shared.data_classes import ConditionValue  # noqa:E402
from app.shared.helpers import find_enum  # noqa:E402


def _build_condition(condition_data, destination_page_path) -> Condition:
    sub_conditions = []
    for c in condition_data["value"]["conditions"]:
        sc = {
            "field": c["field"],
            "value": c["value"],
            "operator": c["operator"],
        }
        if "coordinator" in c and c.get("coordinator"):
            sc["coordinator"] = c.get("coordinator")
        sub_conditions.append(sc)
    condition_value = ConditionValue(name=condition_data["displayName"], conditions=sub_conditions)
    result = Condition(
        name=condition_data["name"],
        display_name=condition_data["displayName"],
        value=condition_value,
        destination_page_path=destination_page_path,
    )
    return result


def _get_component_by_runner_name(db, runner_component_name, page_id):

    return (
        db.session.query(Component)
        .filter(Component.runner_component_name == runner_component_name)
        .filter(Component.page_id == page_id)
        .first()
    )


def add_conditions_to_components(db, page: dict, conditions: dict, page_id):
    # Convert conditions list to a dictionary for faster lookup
    conditions_dict = {cond["name"]: cond for cond in conditions}

    # Initialize a cache for components to reduce database queries
    components_cache = {}

    if "next" in page:
        for path in page["next"]:
            if "condition" in path:
                target_condition_name = path["condition"]
                # Use the conditions dictionary for faster lookup
                if target_condition_name in conditions_dict:
                    condition_data = conditions_dict[target_condition_name]
                    # for condition in condition_data["value"]["conditions"]:
                    runner_component_name = condition_data["value"]["conditions"][0]["field"]["name"]

                    # Use the cache to reduce database queries
                    if runner_component_name not in components_cache:
                        component_to_update = _get_component_by_runner_name(db, runner_component_name, page_id)
                        components_cache[runner_component_name] = component_to_update
                    else:
                        component_to_update = components_cache[runner_component_name]

                    # Create a new Condition instance with a different variable name
                    new_condition = _build_condition(condition_data, destination_page_path=path["path"])

                    # Add the new condition to the conditions list of the component to update
                    if component_to_update.conditions:
                        component_to_update.conditions.append(asdict(new_condition))
                    else:
                        component_to_update.conditions = [asdict(new_condition)]


def _find_list_and_create_if_not_existing(list_name: str, all_lists_in_form: list[dict]) -> UUID:
    list_from_form = next(li for li in all_lists_in_form if li["name"] == list_name)

    # Check if this list already exists in the database
    existing_list = get_list_by_name(list_name=list_name)
    if existing_list:
        return existing_list.list_id

    # If it doesn't, insert new list
    new_list = insert_list(do_commit=False, list_config={"is_template": True, **list_from_form})
    return new_list.list_id


def insert_component_as_template(component, page_id, page_index, lizts):
    # if component has a list, insert the list into the database
    list_id = None
    component_list = component.get("list", None)
    if component_list:
        list_id = _find_list_and_create_if_not_existing(list_name=component_list, all_lists_in_form=lizts)

    # establish component type
    component_type = component.get("type", None)
    if component_type is None or find_enum(ComponentType, component_type) is None:
        raise ValueError(f"Component type not found: {component_type}")
    else:
        confirmed_component_type = find_enum(ComponentType, component_type)

    new_component = Component(
        page_id=page_id,
        theme_id=None,
        title=component.get("title", None),
        content=component.get("content", None),
        hint_text=component.get("hint", None),
        options=component.get("options", None),
        type=confirmed_component_type,
        template_name=component.get("title"),
        is_template=True,
        page_index=page_index,
        # theme_index=component.get('theme_index', None), TODO: add theme_index to json
        runner_component_name=component.get("name", None),
        list_id=list_id,
        children=component.get("children", None),
        schema=component.get("schema", None)
    )
    try:
        db.session.add(new_component)
    except Exception as e:
        print(e)
        raise e
    return new_component


def insert_page_as_template(page, form_id):
    new_page = Page(
        form_id=form_id,
        display_path=page.get("path").lstrip("/"),
        form_index=None,
        name_in_apply_json={"en": page.get("title")},
        controller=page.get("controller", None),
        is_template=True,
        template_name=page.get("title", None),
    )
    try:
        db.session.add(new_page)
    except Exception as e:
        print(e)
        raise e
    return new_page


def find_page_by_path(path):
    page = db.session.query(Page).filter(Page.display_path == path.lstrip("/")).first()
    return page


def insert_page_default_next_page(pages_config, db_pages):
    for current_page_config in pages_config:
        for db_page in db_pages:
            if db_page.display_path == current_page_config.get("path").lstrip("/"):
                current_db_page = db_page
        page_nexts = current_page_config.get("next", [])
        next_page_path_with_no_condition = next((p for p in page_nexts if not p.get("condition")), None)
        if not next_page_path_with_no_condition:
            # no default next page so move on (next page is based on conditions)
            continue

        # set default next page id
        for db_page in db_pages:
            if db_page.display_path == next_page_path_with_no_condition.get("path").lstrip("/"):
                current_db_page.default_next_page_id = db_page.page_id
        # Update the page in the database
        db.session.add(current_db_page)
    db.session.flush()


def insert_form_config(form_config, form_id):
    inserted_pages = []
    inserted_components = []
    start_page_path = form_config["startPage"]
    for page in form_config.get("pages", []):
        if page["path"] == start_page_path:
            page["controller"] = "start.js"
        inserted_page = insert_page_as_template(page, form_id)
        inserted_pages.append(inserted_page)
        db.session.flush()  # flush to get the page id
        for c_idx, component in enumerate(page.get("components", [])):
            inserted_component = insert_component_as_template(
                component, inserted_page.page_id, (c_idx + 1), form_config["lists"]
            )
            inserted_components.append(inserted_component)
        db.session.flush()  # flush to make components available for conditions
        add_conditions_to_components(db, page, form_config["conditions"], inserted_page.page_id)
    insert_page_default_next_page(form_config.get("pages", None), inserted_pages)
    db.session.flush()
    return inserted_pages, inserted_components


def insert_form_as_template(form, template_name=None):
    start_page_path = form.get("startPage")
    if "name" in form:
        form_name = form.get("name")
    else:
        # If form doesn't have a name element, use the title of the start page
        form_name = next(p for p in form["pages"] if p["path"] == start_page_path)["title"]
    if not template_name:
        template_name = form["filename"].split(".")[0]
    new_form = Form(
        section_id=None,
        name_in_apply_json={"en": form_name},
        template_name=template_name,
        is_template=True,
        audit_info=None,
        section_index=None,
        runner_publish_name=human_to_kebab_case(form_name),
        source_template_id=None,
    )

    try:
        db.session.add(new_form)
    except Exception as e:
        print(e)
        raise e

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
            # prepare all row commits
            inserted_form = insert_form_as_template(form_config)
            db.session.flush()  # flush to get the form id
            inserted_pages, inserted_components = insert_form_config(form_config, inserted_form.form_id)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        raise e


def load_json_from_file(data, template_name):
    db = app.extensions["sqlalchemy"]
    try:
        data["filename"] = human_to_kebab_case(template_name)
        inserted_form = insert_form_as_template(data, template_name=template_name)
        db.session.flush()  # flush to get the form id
        insert_form_config(data, inserted_form.form_id)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        raise e


if __name__ == "__main__":
    with app.app_context():
        load_form_jsons()
