# pip install pandas openpyxl

import json
import os
import sys

sys.path.insert(1, ".")
from dataclasses import asdict  # noqa:E402

from app.app import app  # noqa:E402
from app.db.models import Component  # noqa:E402
from app.db.models import ComponentType  # noqa:E402
from app.db.models import Form  # noqa:E402
from app.db.models import Lizt  # noqa:E402
from app.db.models import Page  # noqa:E402
from app.db.models import Section  # noqa:E402
from app.shared.data_classes import Condition  # noqa:E402
from app.shared.helpers import find_enum  # noqa:E402


def add_conditions_to_components(db, page, conditions):
    # Convert conditions list to a dictionary for faster lookup
    conditions_dict = {cond["name"]: cond for cond in conditions}

    # Initialize a cache for components to reduce database queries
    components_cache = {}

    for path in page["next"]:
        if "condition" in path:
            target_condition_name = path["condition"]
            # Use the conditions dictionary for faster lookup
            if target_condition_name in conditions_dict:
                condition_data = conditions_dict[target_condition_name]
                runner_component_name = condition_data["value"]["conditions"][0]["field"]["name"]

                # Use the cache to reduce database queries
                if runner_component_name not in components_cache:
                    component_to_update = (
                        db.session.query(Component)
                        .filter(Component.runner_component_name == runner_component_name)
                        .first()
                    )
                    components_cache[runner_component_name] = component_to_update
                else:
                    component_to_update = components_cache[runner_component_name]

                # Create a new Condition instance with a different variable name
                new_condition = Condition(
                    name=condition_data["value"]["name"],
                    value=condition_data["value"]["conditions"][0]["value"]["value"],
                    operator=condition_data["value"]["conditions"][0]["operator"],
                    destination_page_path=path["path"],
                )

                # Add the new condition to the conditions list of the component to update
                if component_to_update.conditions:
                    component_to_update.conditions.append(asdict(new_condition))
                else:
                    component_to_update.conditions = [asdict(new_condition)]


def insert_component_as_template(component, page_id, page_index, lizts):
    # if component has a list, insert the list into the database
    list_id = None
    component_list = component.get("list", None)
    if component_list:
        for li in lizts:
            if li["name"] == component_list:
                new_list = Lizt(
                    is_template=True,
                    name=li.get("name"),
                    title=li.get("title"),
                    type=li.get("type"),
                    items=li.get("items"),
                )
                try:
                    db.session.add(new_list)
                except Exception as e:
                    print(e)
                    raise e
                db.session.flush()  # flush to get the list id
                list_id = new_list.list_id
                break

    new_component = Component(
        page_id=page_id,
        theme_id=None,
        title=component.get("title", ""),
        hint_text=component.get("hint", None),
        options=component.get("options", None),
        type=find_enum(ComponentType, component.get("type", None)),
        template_name=component.get("title"),
        is_template=True,
        page_index=page_index,
        # theme_index=component.get('theme_index', None), TODO: add theme_index to json
        runner_component_name=component.get("name", ""),
        list_id=list_id,
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


def insert_form_config(form_config, form_id, db):
    inserted_pages = []
    inserted_components = []
    for page in form_config.get("pages", []):
        inserted_page = insert_page_as_template(page, form_id)
        inserted_pages.append(inserted_page)
        db.session.flush()  # flush to get the page id
        for c_idx, component in enumerate(page.get("components", [])):
            inserted_component = insert_component_as_template(
                component, inserted_page.page_id, (c_idx + 1), form_config["lists"]
            )
            inserted_components.append(inserted_component)
        db.session.flush()  # flush to make components available for conditions
        add_conditions_to_components(db, page, form_config["conditions"])
    insert_page_default_next_page(form_config.get("pages", None), inserted_pages)
    db
    return inserted_pages, inserted_components


def insert_form_as_template(form, db):
    section = db.session.query(Section.section_id).first()
    new_form = Form(
        section_id=section.section_id,
        name_in_apply_json={"en": form.get("name")},
        template_name=form.get("name"),
        is_template=True,
        audit_info=None,
        section_index=None,
        runner_publish_name=filename,
        source_template_id=None,
    )

    try:
        db.session.add(new_form)
    except Exception as e:
        print(e)
        raise e

    return new_form


def read_json(filename):
    script_dir = os.path.dirname(__file__)
    # Construct the path to the Excel file relative to the script's location
    file_name = os.path.join(script_dir, filename)
    # Read json file into python dict
    with open(file_name, "r") as json_file:
        form = json.load(json_file)
    return form


if __name__ == "__main__":
    with app.app_context():
        try:
            db = app.extensions["sqlalchemy"]
            filename = "asset-information-cof-r3-w2.json"
            form_config = read_json(filename)
            # prepare all row commits
            inserted_form = insert_form_as_template(form_config, db)
            db.session.flush()  # flush to get the form id
            inserted_pages, inserted_components = insert_form_config(form_config, inserted_form.form_id, db)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            raise e
