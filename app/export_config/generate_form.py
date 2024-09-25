import copy

from app.db.models import Component
from app.db.models import Form
from app.db.models import Page
from app.db.models.application_config import READ_ONLY_COMPONENTS
from app.db.models.application_config import ComponentType
from app.db.queries.application import get_list_by_id

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


def build_conditions(component: Component) -> list:
    """
    Takes in a simple set of conditions and builds them into the form runner format
    """
    results = []
    for condition in component.conditions:
        condition_entry = {
            "field": {
                "name": component.runner_component_name,
                "type": component.type.value,
                "display": component.title,
            },
            "operator": condition["operator"],
            "value": condition["value"],
        }

        # Add 'coordinator' only if it exists
        if condition.get("coordinator"):
            condition_entry["coordinator"] = condition.get("coordinator")

        if condition["name"] in [c["name"] for c in results]:
            # If this condition already exists, add it to the existing condition
            existing_condition = next(c for c in results if c["name"] == condition["name"])
            existing_condition["value"]["conditions"].append(condition_entry)
            continue

        result = {
            "displayName": condition["display_name"],
            "name": condition["name"],
            "value": {
                "name": condition["display_name"],
                "conditions": [condition_entry],
            },
        }

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
            "schema": {},
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
            "schema": {},
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
    # Having a 'null' controller element breaks the form-json, needs to not be there if blank
    if page.controller:
        built_page["controller"] = page.controller

    for component in page.components:
        built_component = build_component(component)

        built_page["components"].append(built_component)

    return built_page


# Goes through the set of pages and updates the conditions and next properties to account for branching
def build_navigation(partial_form_json: dict, input_pages: list[Page]) -> dict:
    for page in input_pages:
        # find page in prepared output results
        this_page_in_results = next(p for p in partial_form_json["pages"] if p["path"] == f"/{page.display_path}")

        if page.controller and page.controller.endswith("summary.js"):
            continue
        next_page_id = page.default_next_page_id
        if next_page_id:
            find_next_page = lambda id: next(p for p in input_pages if p.page_id == id)  # noqa:E731
            default_next_page = find_next_page(next_page_id)
            next_path = default_next_page.display_path
            # add the default next page
            this_page_in_results["next"].append({"path": f"/{next_path}"})
        else:
            # all page paths are conditionals which will be processed later
            next_path = None

        has_conditions = False
        for component in page.components:
            if not component.conditions:
                continue
            form_json_conditions = build_conditions(component)
            has_conditions = True
            partial_form_json["conditions"].extend(form_json_conditions)

            for condition in component.conditions:
                if condition["destination_page_path"] == "CONTINUE":
                    destination_path = f"/{next_path}"
                else:
                    destination_path = f"/{condition['destination_page_path'].lstrip('/')}"

                this_page_in_results["next"].append(
                    {
                        "path": destination_path,
                        "condition": condition["name"],
                    }
                )

        if not has_conditions and not next_path:
            this_page_in_results["next"].append({"path": "/summary"})

    return partial_form_json


def build_lists(pages: list[dict]) -> list:
    # Takes in the form builder format json and copies in any lists used in those pages
    lists = []
    for page in pages:
        for component in page["components"]:
            if component.get("list"):
                list_from_db = get_list_by_id(component["metadata"]["fund_builder_list_id"])
                list_dict = {
                    "type": list_from_db.type,
                    "items": list_from_db.items,
                    "name": list_from_db.name,
                    "title": list_from_db.title,
                }
                # Check if the list already exists in lists by name
                if not any(existing_list["name"] == list_dict["name"] for existing_list in lists):
                    lists.append(list_dict)
            # Remove the metadata key from component (no longer needed)
            component.pop("metadata", None)  # The second argument prevents KeyError if 'metadata' is not found

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
            "next": [{"path": f"/{form.pages[0].display_path}"}],
        }
    )
    ask_about = "<p class='govuk-body'>We will ask you about:</p> <ul>"
    for page in form.pages:
        ask_about += f"<li>{page.name_in_apply_json['en']}</li>"
    ask_about += "</ul>"

    start_page["components"].append(
        {
            "name": "start-page-content",
            "options": {},
            "type": "Html",
            "content": f"<p class='govuk-body'>{content}</p>{ask_about}",
            "schema": {},
        }
    )
    return start_page


def human_to_kebab_case(word: str) -> str | None:
    """
    Converts the supplied string into all lower case, and replaces spaces with hyphens
    """
    if word:
        return word.replace(" ", "-").strip().lower()


def build_form_json(form: Form) -> dict:
    """
    Takes in a single Form object and then generates the form runner json for that form.

    Inserts a start page to the beginning of the form, and the summary page at the end.
    """

    results = copy.deepcopy(BASIC_FORM_STRUCTURE)
    results["name"] = form.name_in_apply_json["en"]

    # Build the basic page structure
    for page in form.pages:
        results["pages"].append(build_page(page=page))

    # start page is the page with the controller ending start.js
    start_page = _find_page_by_controller(form.pages, "start.js")
    if start_page:
        results["startPage"] = f"/{start_page.display_path}"
    else:
        # Create the start page
        start_page = build_start_page(content=None, form=form)
        results["pages"].append(start_page)
        results["startPage"] = start_page["path"]

    # Build navigation and add any pages from branching logic
    results = build_navigation(results, form.pages)

    # Build the list values
    results["lists"] = build_lists(results["pages"])

    # Add on the summary page
    summary_page = _find_page_by_controller(form.pages, "summary.js")
    if not summary_page:
        results["pages"].append(SUMMARY_PAGE)

    return results
