import copy
from dataclasses import asdict
from typing import Optional

from app.db.models import Component, Condition, Form, Page
from app.db.models.application_config import READ_ONLY_COMPONENTS, ComponentType
from app.db.queries.application import get_list_by_id
from app.export_config.helpers import human_to_kebab_case
from app.shared.data_classes import ConditionValue, FormSection

BASIC_FORM_STRUCTURE = {
    "startPage": None,
    "pages": [],
    "lists": [],
    "conditions": [],
    "sections": [],
    "outputs": [],
    "skipSummary": False,
    "name": "",
}

BASIC_PAGE_STRUCTURE = {
    "path": None,
    "title": None,
    "components": [],
    "next": [],
}


SUMMARY_PAGE = {
    "path": "/summary",
    "title": "Check your answers",
    "components": [],
    "next": [],
    "section": "uLwBuz",
    "controller": "./pages/summary.js",
}


def build_conditions(conditions: list[Condition]) -> list:
    """
    Takes in a simple set of conditions and builds them into the form runner format
    """
    results = []
    for condition in conditions:
        result = {
            "displayName": condition.display_name,
            "name": condition.name,
            "value": asdict(
                ConditionValue(
                    name=condition.value["name"],
                    conditions=[],
                )
            ),
        }
        for sc in condition.value["conditions"]:
            sub_condition = {
                "field": sc["field"],
                "operator": sc["operator"],
                "value": sc["value"],
            }
            # only add coordinator if it exists
            if "coordinator" in sc and sc.get("coordinator") is not None:
                sub_condition["coordinator"] = sc.get("coordinator", None)
            result["value"]["conditions"].append(sub_condition)

        results.append(result)

    return results


def build_component(component: Component) -> dict:
    """
    Builds the component json in form runner format for the supplied Component object
    """
    # Depends on component (if read only type then this needs to be a different structure)

    if component.type in READ_ONLY_COMPONENTS:
        built_component = {
            "type": component.type.value if component.type else None,
            "content": component.content,
            "options": component.options or {},
            "schema": component.schema or {},
            "title": component.title,
            "name": component.runner_component_name,
        }
        # Remove keys with None values (it varies for read only components)
        built_component = {k: v for k, v in built_component.items() if v is not None}
    else:
        built_component = {
            "options": component.options or {},
            "type": component.type.value,
            "title": component.title,
            "hint": component.hint_text or "",
            "schema": component.schema or {},
            "name": component.runner_component_name,
            "metadata": {
                # "fund_builder_id": str(component.component_id) TODO why do we need this?
            },
        }
    # add a reference to the relevant list if this component use a list
    if component.type.value is ComponentType.YES_NO_FIELD.value:
        # implicit list
        built_component.update({"values": {"type": "listRef"}})
    elif component.lizt:
        built_component.update({"list": component.lizt.name})
        built_component["metadata"].update({"fund_builder_list_id": str(component.list_id)})
        built_component.update({"values": {"type": "listRef"}})

    if component.type is ComponentType.MULTI_INPUT_FIELD:
        child_component_config = []
        for child_component in component.children_components:
            child_component_config.append(build_component(child_component))
        built_component.update({"children": child_component_config})

    return built_component


def build_page(page: Page = None) -> dict:
    """
    Builds the form runner JSON structure for the supplied page.

    Then builds all the components on this page and adds them to the page json structure
    """
    built_page = copy.deepcopy(BASIC_PAGE_STRUCTURE)
    built_page.update(
        {
            "path": f"/{page.display_path}",
            "title": page.name_in_apply_json["en"],
        }
    )
    if page.formsection:
        built_page.update({"section": page.formsection.name})
    if page.options:
        built_page.update({"options": page.options})
    # Having a 'null' controller element breaks the form-json, needs to not be there if blank
    if page.controller:
        built_page["controller"] = page.controller

    for component in page.components:
        built_component = build_component(component)
        built_page["components"].append(built_component)

    return built_page


# Goes through the set of pages and updates the conditions and next properties to account for branching
def build_navigation(partial_form_json: dict, form: Form) -> dict:
    partial_form_json["conditions"] = build_conditions(form.conditions) if form.conditions else []

    for page in form.pages:
        if page.controller and page.controller.endswith("summary.js"):
            continue

        this_page_in_results = _get_page_result(partial_form_json, page)
        _add_next_paths(this_page_in_results, page, form)

    return partial_form_json


def _get_page_result(partial_form_json: dict, page: Page) -> dict:
    return next(p for p in partial_form_json["pages"] if p["path"] == f"/{page.display_path}")


def _add_next_paths(this_page_result: dict, page: Page, form: Form) -> None:
    next_path = _get_default_next_path(page, form)
    if next_path:
        this_page_result["next"].append({"path": f"/{next_path}"})

    if page.conditions:
        _add_conditional_paths(this_page_result, page)

    if not page.conditions and not next_path:
        this_page_result["next"].append({"path": "/summary"})


def _get_default_next_path(page: Page, form: Form) -> Optional[str]:
    if not page.default_next_page_id:
        return None
    next_page = next(p for p in form.pages if p.page_id == page.default_next_page_id)
    return next_page.display_path


def _add_conditional_paths(this_page_result: dict, page: Page) -> None:
    for condition in page.conditions:
        for page_condition in filter(lambda pc: pc.page_id == page.page_id, condition.page_conditions):
            this_page_result["next"].append(
                {
                    "path": page_condition.destination_page_path,
                    "condition": condition.name,
                }
            )


def build_form_section(form_section_list, form_section):
    form_section_obj = FormSection(
        name=form_section.name,
        title=form_section.title,
        hideTitle=form_section.hide_title,
    )
    # Check if the list already exists in lists by name
    if not any(existing_list["name"] == form_section_obj.name for existing_list in form_section_list):
        form_section_list.append(form_section_obj.as_dict())


def build_lists(pages: list[dict]) -> list:
    def get_child_components(component: dict) -> list:
        if component.get("type") == "MultiInputField" and component.get("children"):
            return component["children"]
        return [component]

    def process_component(comp: dict, seen_names: set, lists: list):
        metadata = comp.get("metadata")
        if metadata:
            list_from_db = get_list_by_id(metadata.get("fund_builder_list_id"))
            if list_from_db and list_from_db.name not in seen_names:
                lists.append(
                    {
                        "type": list_from_db.type,
                        "items": list_from_db.items,
                        "name": list_from_db.name,
                        "title": list_from_db.title,
                    }
                )
                seen_names.add(list_from_db.name)
        comp.pop("metadata", None)

    lists = []
    seen_names = set()

    for page in pages:
        for component in page["components"]:
            for comp in get_child_components(component):
                process_component(comp, seen_names, lists)

    return lists


def _find_page_by_controller(pages, controller_name) -> dict:
    return next((p for p in pages if p.controller and p.controller.endswith(controller_name)), None)


def build_start_page(content: str, form: Form) -> dict:
    """
    Builds the start page which contains just an html component comprising a bullet
    list of the headings of all pages in this form
    """
    start_page = copy.deepcopy(BASIC_PAGE_STRUCTURE)
    start_page.update(
        {
            "title": form.name_in_apply_json["en"],
            "path": f"/intro-{human_to_kebab_case(form.name_in_apply_json['en'])}",
            "controller": "./pages/start.js",
        }
    )
    ask_about = None
    if len(form.pages) > 0:
        ask_about = '<p class="govuk-body">We will ask you about:</p> <ul>'
        for page in form.pages:
            if page.controller and page.controller.endswith("summary.js"):
                continue
            ask_about += f"<li>{page.name_in_apply_json['en']}</li>"
        ask_about += "</ul>"
        start_page.update(
            {
                "next": [{"path": f"/{form.pages[0].display_path}"}],
            }
        )

    start_page["components"].append(
        {
            "name": "start-page-content",
            "options": {},
            "type": "Html",
            "content": f'<p class="govuk-body">{content or ""}</p>{ask_about or ""}',
            "schema": {},
        }
    )
    return start_page


def build_form_json(form: Form, fund_title: str = None) -> dict:
    """
    Takes in a single Form object and then generates the form runner json for that form.

    Inserts a start page to the beginning of the form, and the summary page at the end.
    """

    results = copy.deepcopy(BASIC_FORM_STRUCTURE)
    results["name"] = f"Apply for {fund_title}" if fund_title else "Access Funding"
    results["sections"] = []
    # Build the basic page structure
    for page in form.pages:
        results["pages"].append(build_page(page=page))
        if page.formsection:
            build_form_section(results["sections"], page.formsection)

    # start page is the page with the controller ending start.js
    start_page = _find_page_by_controller(form.pages, "./pages/start.js")
    if start_page:
        results["startPage"] = f"/{start_page.display_path}"
    else:
        # Create the start page
        start_page = build_start_page(content=None, form=form)
        results["pages"].append(start_page)
        results["startPage"] = start_page["path"]

    # Build navigation and add any pages from branching logic
    results = build_navigation(results, form)

    # Build the list values
    results["lists"] = build_lists(results["pages"])

    # Add on the summary page
    summary_page = _find_page_by_controller(form.pages, "summary.js")
    if not summary_page:
        results["pages"].append(SUMMARY_PAGE)

    return results
