# pip install pandas openpyxl

import json
import os
import sys
from uuid import UUID

from app.db.queries.application import insert_condition, insert_form_section, insert_list, insert_page_condition
from app.shared.helpers import human_to_kebab_case

sys.path.insert(1, ".")

from app.create_app import app  # noqa:E402
from app.db import db  # noqa:E402
from app.db.models import (
    Component,  # noqa:E402
    ComponentType,  # noqa:E402
    Page,  # noqa:E402
)
from app.db.queries.application import insert_new_form  # noqa:E402
from app.shared.data_classes import (
    Condition,  # noqa:E402
    ConditionValue,  # noqa:E402
)
from app.shared.helpers import (
    find_enum,  # noqa:E402
)


def _build_condition(condition_data, source_page_path, destination_page_path) -> Condition:
    """
    Build a Condition instance from the given condition data

    Args:
        condition_data (dict): The condition data to build the Condition instance from
        source_page_path (str): The path of the source page.
            Sometimes the conditions component that is referenced is on another page,
            so we need to retain the page using the condition.
        destination_page_path (str): The path of the destination page

    Returns:
        Condition: The built Condition instance

    """
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
        source_page_path=source_page_path,
        destination_page_path=destination_page_path,
    )
    return result


def _get_component_by_runner_name(db, runner_component_name, page_ids: list):
    return (
        db.session.query(Component)
        .filter(Component.runner_component_name == runner_component_name)
        .filter(Component.page_id.in_(page_ids))
        .first()
    )


def add_conditions_to_pages(page: dict, page_id, conditions_map: dict):
    if "next" in page:
        for path in page["next"]:
            if "condition" in path:
                insert_page_condition(
                    condition_id=conditions_map.get(path.get("condition"), None), page_id=page_id, path=path.get("path")
                )


def _find_form_section(form_section_name: str, form_section_list: list[dict]) -> UUID:
    form_section_to_search = form_section_name if form_section_name else "FabDefault"
    form_section_from_db = next(
        form_section for form_section in form_section_list if form_section.name == form_section_to_search
    )
    return form_section_from_db.form_section_id


def insert_component_as_template(component, page_id, page_index, list_names_to_ids):
    # if component has a list, get the list ID
    list_id = list_names_to_ids.get(component.get("list"), None)

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
        schema=component.get("schema", None),
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
        options=page.get("options", None),
        form_section_id=page.get("section", None),
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


def create_form_sections_db(form_config):
    form_section_list = []
    for form_section in form_config["sections"]:
        form_section_list.append(
            insert_form_section(do_commit=False, form_section_config={"is_template": True, **form_section})
        )
    # create default section if any of the page doesn't have section
    page_exists_without_section = any(page.get("section", None) is None for page in form_config["pages"])
    if page_exists_without_section:
        section_info = {"name": "FabDefault", "title": "Default section", "hideTitle": True}
        form_section_list.append(
            insert_form_section(do_commit=False, form_section_config={"is_template": True, **section_info})
        )
    return form_section_list


def insert_form_config(form_config, form_id):
    inserted_pages = []
    inserted_components = []
    form_section_list = create_form_sections_db(form_config)

    list_names_to_ids = {}
    for lizt in form_config.get("lists", []):
        new_list = insert_list(do_commit=False, list_config={"is_template": True, **lizt})
        list_names_to_ids[lizt["name"]] = new_list.list_id

    conditions_map = {}
    for condition in form_config.get("conditions", []):
        condition = insert_condition(
            form_id=form_id, do_commit=False, condition_config={"is_template": True, **condition}
        )
        conditions_map[condition.name] = condition.condition_id

    for page in form_config.get("pages", []):
        form_section = page.get("section", None)
        # fetch the form section_id  from db
        form_section_id = _find_form_section(form_section, form_section_list)
        page["section"] = form_section_id
        inserted_page = insert_page_as_template(page, form_id)
        inserted_pages.append(inserted_page)
        db.session.flush()  # flush to get the page id
        for c_idx, component in enumerate(page.get("components", [])):
            inserted_component = insert_component_as_template(
                component, inserted_page.page_id, (c_idx + 1), list_names_to_ids
            )
            if inserted_component.type == ComponentType.MULTI_INPUT_FIELD:
                for children_component_idx, child_component in enumerate(component.get("children", [])):
                    inserted_child_component = insert_component_as_template(
                        child_component, None, (children_component_idx + 1), list_names_to_ids
                    )
                    inserted_child_component.parent_component = inserted_component
                    inserted_components.append(inserted_child_component)
            inserted_components.append(inserted_component)
        db.session.flush()  # flush to make components available for conditions
        add_conditions_to_pages(page, inserted_page.page_id, conditions_map)

    db.session.flush()

    insert_page_default_next_page(form_config.get("pages", None), inserted_pages)
    db.session.commit()
    return inserted_pages, inserted_components


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
            # prepare all row commits
            inserted_form = insert_form_as_template(form_config, None, form_config["filename"])
            inserted_pages, inserted_components = insert_form_config(form_config, inserted_form.form_id)
    except Exception as e:
        print(e)
        db.session.rollback()
        raise e


def load_json_from_file(data, template_name, filename):
    db = app.extensions["sqlalchemy"]
    try:
        data["filename"] = human_to_kebab_case(template_name)
        inserted_form = insert_form_as_template(data, template_name=template_name, filename=filename)
        db.session.flush()  # flush to get the form id
        insert_form_config(data, inserted_form.form_id)
        db.session.commit()
        return inserted_form
    except Exception as e:
        print(e)
        db.session.rollback()
        raise e


if __name__ == "__main__":
    with app.app_context():
        load_form_jsons()
