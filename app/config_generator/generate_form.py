import copy

from app.db.models import Component
from app.db.models import Form
from app.db.models import Page
from app.db.queries.application import get_list_by_id
from app.db.queries.application import get_template_page_by_display_path

BASIC_FORM_STRUCTURE = {
    "metadata": {},
    "startPage": None,
    "backLinkText": "Go back to application overview",
    "pages": [],
    "lists": [],
    "conditions": [],
    "fees": [],
    "sections": [],
    "outputs": [
        {
            "name": "update-form",
            "title": "Update form in application store",
            "type": "savePerPage",
            "outputConfiguration": {"savePerPageUrl": True},
        }
    ],
    "skipSummary": False,
    "name": "",
}

BASIC_PAGE_STRUCTURE = {
    "path": None,
    "title": None,
    "components": [],
    "next": [],
    "options": {},
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
        result = {
            "displayName": condition["name"],
            "name": condition["name"],
            "value": {
                "name": condition["name"],
                "conditions": [
                    {
                        "field": {
                            "name": component.runner_component_name,
                            "type": component.type.value,
                            "display": component.title,
                        },
                        "operator": condition["operator"],
                        "value": {
                            "type": "Value",
                            "value": condition["value"],
                            "display": condition["value"],
                        },
                    }
                ],
            },
        }
        results.append(result)

    return results


def build_component(component: Component) -> dict:
    """
    Builds the component json in form runner format for the supplied Component object
    """
    built_component = {
        "options": component.options or {},
        "type": component.type.value,
        "title": component.title,
        "hint": component.hint_text or "",
        "schema": {},
        "name": component.runner_component_name,
        "metadata": {"fund_builder_id": str(component.component_id)},
    }
    # add a reference to the relevant list if this component use a list
    if component.lizt:
        built_component.update({"list": component.lizt.name})
        built_component["metadata"].update({"fund_builder_list_id": str(component.list_id)})
    return built_component


def build_page(page: Page = None, page_display_path: str = None) -> dict:
    """
    Builds the form runner JSON structure for the supplied page. If that page is None, retrieves a template
    page with the display_path matching page_display_path.

    This accounts for conditional logic where the destination target will be the display path of a template
    page, but that page does not actually live in the main hierarchy as branching logic uses a fixed set of
    conditions at this stage.

    Then builds all the components on this page and adds them to the page json structure
    """
    if not page:
        page = get_template_page_by_display_path(page_display_path)
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
    # TODO order by index not order in list
    # Think this is sorted now that the collection is sorted by index, but needs testing
    for i in range(0, len(input_pages)):
        if i < len(input_pages) - 1:
            next_path = input_pages[i + 1].display_path
        elif i == len(input_pages) - 1:
            next_path = "summary"
        else:
            next_path = None

        this_page = input_pages[i]
        this_page_in_results = next(p for p in partial_form_json["pages"] if p["path"] == f"/{this_page.display_path}")

        has_conditions = False

        for component in this_page.components:
            if not component.conditions:
                continue
            form_json_conditions = build_conditions(component)
            has_conditions = True
            partial_form_json["conditions"].extend(form_json_conditions)

            for condition in component.conditions:
                if condition["destination_page_path"] == "CONTINUE":
                    destination_path = f"/{next_path}"
                else:
                    destination_path = f"/{condition['destination_page_path']}"

                # If this points to a pre-built page flow, add that in now (it won't be in the input)
                if (
                    destination_path not in [page["path"] for page in partial_form_json["pages"]]
                    and not destination_path == "/summary"
                ):
                    sub_page = build_page(page_display_path=destination_path[1:])
                    if not sub_page.get("next", None):
                        sub_page["next"] = [{"path": f"/{next_path}"}]

                    partial_form_json["pages"].append(sub_page)

                this_page_in_results["next"].append(
                    {
                        "path": destination_path,
                        "condition": condition["name"],
                    }
                )

        # If there were no conditions we just continue to the next page
        if not has_conditions:
            this_page_in_results["next"].append({"path": f"/{next_path}"})

    return partial_form_json


def build_lists(pages: list[dict]) -> list:
    # Takes in the form builder format json and copies in any lists used in those pages
    lists = []
    for page in pages:
        for component in page["components"]:
            if component.get("list"):
                list_from_db = get_list_by_id(component["metadata"]["fund_builder_list_id"])
                list = {"type": list_from_db.type, "items": list_from_db.items, "name": list_from_db.name}
                lists.append(list)

    return lists


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
    ask_about = '<p class="govuk-body">We will ask you about:</p> <ul>'
    for page in form.pages:
        ask_about += f"<li>{page.name_in_apply_json['en']}</li>"
    ask_about += "</ul>"

    start_page["components"].append(
        {
            "name": "start-page-content",
            "options": {},
            "type": "Html",
            "content": f'<p class="govuk-body">{content}</p>{ask_about}',
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

    # Create the start page
    start_page = build_start_page(content=None, form=form)
    results["pages"].append(start_page)
    results["startPage"] = start_page["path"]

    # Build navigation and add any pages from branching logic
    results = build_navigation(results, form.pages)

    # Build the list values
    results["lists"] = build_lists(results["pages"])

    # Add on the summary page
    results["pages"].append(SUMMARY_PAGE)

    return results
