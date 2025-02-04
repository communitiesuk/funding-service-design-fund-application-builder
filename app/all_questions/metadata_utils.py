import copy
import fnmatch
from typing import Tuple

from bs4 import BeautifulSoup, NavigableString

from app.all_questions.read_forms import (
    build_section_header,
    determine_display_value_for_condition,
    determine_if_just_html_page,
    increment_lowest_in_hierarchy,
    remove_lowest_in_hierarchy,
    strip_leading_numbers,
)

FIELD_TYPES_WITH_MAX_WORDS = ["freetextfield", "multilinetextfield"]


def get_all_child_nexts(page: dict, child_nexts: list, all_pages: dict):
    """Recursively builds a list of everything that could come next from this page,
    and then everything that could come next from those next pages, and so on.


    Args:
        page (dict): _description_
        child_nexts (list): _description_
        all_pages (dict): _description_
    """
    # TODO write tests
    child_nexts.update([n for n in page["next_paths"]])
    for next_page_path in page["next_paths"]:
        next_page = next(p for p in all_pages if p["path"] == next_page_path)
        get_all_child_nexts(next_page, child_nexts, all_pages)


def get_all_possible_previous(page_path: str, results: list, all_pages: dict):
    """Recursively finds all pages that could have come before this one, in any branch of questions

    Args:
        page_path (str): _description_
        results (list): _description_
        all_pages (dict): _description_
    """

    # TODO write tests
    direct_prev = [prev["path"] for prev in all_pages if page_path in prev["next_paths"]]
    results.update(direct_prev)
    for prev in direct_prev:
        get_all_possible_previous(prev, results, all_pages)


def generate_metadata(full_form_data: dict) -> dict:
    """Generates metadata for a form. Basically a dict containing the following:
    ```
    {
    "start_page": "/intro-about-your-organisation",
    "all_pages": [
        {
            "path": "/organisation-details",
            "next_paths": [
                Everything that could come directly after this page
            ],
            "all_direct_previous": [
                Everything that could come directly (immediately) before this page
            ],
            "direct_next_of_direct_previous": [
                Everything that could come immediately after the pages that lead directly to this one
                (ie this pages siblings)
            ],
            "all_possible_next_of_siblings": [
                Everything that could come any point after any of this pages siblings
            ],
            "all_possible_previous": [
                Everthing that could come at any point before this page
            ],
            "all_possible_previous_direct_next": [
                Everything that could come anywhere before the pages that come directly after this one
            ],
            "all_possible_after": [
                Everything that could come anywhere after this page
            ]
        },
    ]
    ```

    Args:
        full_form_data (dict): Data from the form json file

    Returns:
        dict: The metadata, as described above
    """

    cutdown = {"start_page": full_form_data["startPage"], "all_pages": []}
    for page in full_form_data["pages"]:
        cp = {"path": page["path"], "next_paths": [p["path"] for p in page["next"]]}
        cutdown["all_pages"].append(cp)

    metadata = copy.deepcopy(cutdown)
    for p in metadata["all_pages"]:
        # everything that could come immediately before this page
        p["all_direct_previous"] = [prev["path"] for prev in cutdown["all_pages"] if p["path"] in prev["next_paths"]]

        # all the immediate next paths of the direct previous (aka siblings)
        direct_next_of_direct_previous = set()
        for direct_prev in p["all_direct_previous"]:
            prev_page = next(prev for prev in cutdown["all_pages"] if prev["path"] == direct_prev)
            direct_next_of_direct_previous.update(prev_page["next_paths"])
        p["direct_next_of_direct_previous"] = list(direct_next_of_direct_previous)

        # get all the descendents (possible next anywhere after) of the siblings
        all_possible_next_of_siblings = set()
        for sibling in p["direct_next_of_direct_previous"]:
            sibling_page = next(page for page in cutdown["all_pages"] if page["path"] == sibling)
            get_all_child_nexts(sibling_page, all_possible_next_of_siblings, cutdown["all_pages"])
        p["all_possible_next_of_siblings"] = list(all_possible_next_of_siblings)

        # everything that could come anywhere before this page
        all_possible_previous = set()
        get_all_possible_previous(p["path"], all_possible_previous, cutdown["all_pages"])
        p["all_possible_previous"] = list(all_possible_previous)

        # get everything that is directly after all the possible previous to this page
        all_possible_previous_direct_next = set()
        for prev in p["all_possible_previous"]:
            prev_page = next(page for page in cutdown["all_pages"] if page["path"] == prev)
            all_possible_previous_direct_next.update(prev_page["next_paths"])
        p["all_possible_previous_direct_next"] = list(all_possible_previous_direct_next)

        # everything that could come after this page
        all_possible_after = set()
        get_all_child_nexts(page=p, child_nexts=all_possible_after, all_pages=cutdown["all_pages"])
        p["all_possible_after"] = list(all_possible_after)

    return metadata


def build_hierarchy_levels_for_page(page: dict, results: dict, idx: int, all_pages: dict, start_page: bool = False):
    """Recursively builds up a dict containing the path of each page, and it's level in the hierarchy of the page
    Format of results:
    ```
        {
            "/path-to-page-1": 1,
            "/path-to-sub-page": 2,
            "/path-to-page-2": 1,
            "/path-to-another-sub-page": 2,
        }
    ```

    Args:
        page (dict): Page object from metadata
        results (dict): The dict that will store the hierarchy results
        idx (int): The hierarchy level of this page at this point in the tree
        all_pages (dict): All the pages in the form
        start_page (bool, optional): Whether or not this is the first page in the form. Defaults to False.
    """
    current_level_in_results = results.get(page["path"], 9999)
    # We want the lowest level the page appears at, so only update if we are at it's lowest point
    if idx < current_level_in_results:
        results[page["path"]] = idx

    # loop through every page that comes after this page
    for next_path in [n for n in page["next_paths"]]:
        # default is same level
        next_idx = idx
        next_page = next(p for p in all_pages if p["path"] == next_path)

        # if we have more than one possible next page, go to next level
        if len(page["next_paths"]) > 1 or start_page is True:
            next_idx = idx + 1

        # if this next path is also a next path of the immediate previous, go back a level
        elif next_path in page["direct_next_of_direct_previous"]:
            next_idx = idx - 1

        elif next_path in page["all_possible_previous_direct_next"]:
            next_idx = idx - 1

        # if this page and all it's siblings eventually go back to this same next page, go back a level
        elif len(page["direct_next_of_direct_previous"]) <= 1:
            pass
        elif len(next_page["all_direct_previous"]) == 1:
            pass
        else:
            # Determine whether this next page is the return point for this page and all it's siblings
            is_in_descendents_of_all_siblings = True
            for sibling in page["direct_next_of_direct_previous"]:
                # don't look at this page
                if sibling == page["path"]:
                    continue
                sibling_page = next(p for p in all_pages if p["path"] == sibling)
                if next_path not in sibling_page["all_possible_after"]:
                    is_in_descendents_of_all_siblings = False

            if is_in_descendents_of_all_siblings:
                next_idx = idx - 1

        build_hierarchy_levels_for_page(next_page, results, next_idx, all_pages)


def strip_string_and_append_if_not_empty(string_to_check: str, list_to_append: list):
    """Uses `str.strip()` to remove leading/trailing whitespace from `string_to_check`.
    If the resulting string is not empty, appends this to `list_to_append`

    Args:
        string_to_check (str): String to strip and append
        list_to_append (list): List to append to
    """
    stripped = string_to_check.strip()
    if stripped:
        list_to_append.append(stripped)


def extract_from_html(soup, results: list):
    """
    Takes in a BeautifulSoup element, recursively iterates through it's children to generate text items
    for rendering in the all questions page.

    Any non-empty strings are stripped of leading/trailing spaces etc and appended to `results`.
    Any <ul> elements have their child <li> elements put into a separate list and that list is appended to `results`

    Args:
        soup (_type_): HTML to extract from
        results (list): results to append to
    """
    for element in soup.children:
        # If it's just a string, append that text
        if isinstance(element, NavigableString):
            strip_string_and_append_if_not_empty(element.text, results)
            continue

        # If it's a list, append the list items as another list
        if element.name == "ul":
            bullets = []
            for li in element.children:
                strip_string_and_append_if_not_empty(li.text, bullets)
            results.append(bullets)
            continue

        extract_from_html(element, results)


def update_wording_for_multi_input_fields(text: list) -> list:
    text_to_filter = [item for item in text if not isinstance(item, list)]
    result = fnmatch.filter(text_to_filter, "You can add more * on the next step*")
    if len(result) > 0:
        text.remove(*result)
    return text


def determine_title_and_text_for_component(
    component: dict,
    include_html_components: bool = True,
    form_lists: list = None,
    is_child: bool = False,
) -> Tuple[str, list]:
    """Determines the title and text to display for an individual component.

    Args:
        component (dict): The component to get the text for
        include_html_components (bool, optional): Whether to include html-only components. Defaults to True.
        form_lists (list, optional): All lists in this form - used to determine display values for list items.
            Defaults to [].
        is_child (bool, optionsl): Whether this is a child field in a multi-input field. Defaults to False.


    Returns:
        Tuple[str, list]: First item is the title, second is the text to display
    """
    if form_lists is None:
        form_lists = []
    title: str = component["title"] if "title" in component else None
    text = []
    # skip details, eg about-your-org-cyp GNpQfE
    if component["type"].casefold() == "details":
        return None, []

    # For MultiInputFields, don't add a title and treat each child as a separate component
    if component["type"].casefold() == "multiinputfield":
        title = f"You can add multiple {component['title'].lower()}"
        for child in component["children"]:
            child_title, child_text = determine_title_and_text_for_component(
                child, include_html_components, form_lists, is_child=True
            )
            if child["type"].casefold() in FIELD_TYPES_WITH_MAX_WORDS:
                first_column_title = component["options"]["columnTitles"][0].casefold()
                text.append(f"{child_title} (Max {child['options']['maxWords']} words per {first_column_title})")
            else:
                text.append(child_title)
            text.extend(child_text)

    # Skip pages that are just html, eg about-your-org-cyp uLwBuz
    elif (
        include_html_components
        and ("type" in component)
        and (component["type"].casefold() == "html" or component["type"].casefold() == "para")
    ) or ("hint" in component):
        # If there is hint or content text, extract it from the html in the hint field
        soup = BeautifulSoup(
            component["hint"] if "hint" in component else component["content"],
            "html.parser",
        )
        text = []
        extract_from_html(soup, text)
        update_wording_for_multi_input_fields(text)

    if (
        component["type"].casefold() in FIELD_TYPES_WITH_MAX_WORDS
        and not is_child
        and "maxWords" in component["options"]
    ):
        text.append(f"(Max {component['options']['maxWords']} words)")

    if "list" in component:
        # include available options for lists
        list_id = component["list"]
        list_items = next(list["items"] for list in form_lists if list["name"] == list_id)
        list_display = [item["text"] for item in list_items]
        text.append(list_display)
    return title, text


def build_components_from_page(
    full_page_json: dict,
    include_html_components: bool = True,
    form_lists: list = None,
    form_conditions: list = None,
    index_of_printed_headers: dict = None,
    lang: str = "en",
) -> list:
    """Builds a list of the components to display from this page, including their title and text, and
        directional text on which page to go to next if the form branches from here

    Args:
        full_page_json (dict): This page from the form_jsons data
        include_html_components (bool, optional): Whether or not to include components that are just HTML.
            Defaults to True.
        form_lists (list, optional): The lists that appear in this form. Defaults to [].
        form_conditions (list, optional): The conditions that appear in this form. Defaults to [].
        index_of_printed_headers (dict, optional): The set of pages and their numbers for display, used in
            directing people to another section when branching. Defaults to {}.
        lang (str): Language for display. Defaults to 'en'.

    Returns:
        list: List of components to display, each component being a dict:
            ```
            {
                "title": str,
                "text": str,
                "hide_title": bool
            }
            ```
    """
    # Find out which components in this page determine, through conditions, where we go next
    if index_of_printed_headers is None:
        index_of_printed_headers = {}
    if form_conditions is None:
        form_conditions = []
    if form_lists is None:
        form_lists = []
    components_with_conditions = []
    for condition in form_conditions:
        components_with_conditions.extend([value["field"]["name"] for value in condition["value"]["conditions"]])

    components = []
    for c in full_page_json["components"]:
        title, text = determine_title_and_text_for_component(
            c, include_html_components=include_html_components, form_lists=form_lists
        )
        field_type = c["type"]
        if not title and not text:
            continue

        # If there are multiple options for the next page, include text about where to go next
        if c["name"] in components_with_conditions:
            for next_config in full_page_json["next"]:
                if "condition" in next_config and next_config["path"] != "/summary":
                    condition_name = next_config["condition"]
                    condition_config = next(fc for fc in form_conditions if fc["name"] == condition_name)
                    destination = index_of_printed_headers[next_config["path"]]["title"]
                    text_with_coordinators = ""
                    for condition in [
                        cc for cc in condition_config["value"]["conditions"] if cc["field"]["name"] == c["name"]
                    ]:
                        condition_value = condition["value"]["value"]
                        condition_text = determine_display_value_for_condition(
                            condition_value,
                            list_name=c["list"] if "list" in c else None,
                            form_lists=form_lists,
                            lang=lang,
                        )
                        if condition.get("coordinator"):
                            text_with_coordinators += f" {condition.get('coordinator')} "
                        text_with_coordinators += f"'{condition_text}'"
                    text.append(
                        f"If {text_with_coordinators}, go to <strong>{destination}</strong>"
                        if lang == "en"
                        else (f"Os '{condition_text}', ewch i <strong>{destination}</strong>")
                    )

        component = {
            "title": title,
            "text": text,
            "hide_title": c["options"]["hideTitle"] if "hideTitle" in c["options"] else False,
            "type": field_type,
        }
        components.append(component)
    return components


def generate_print_headings_for_page(
    page: dict,
    form_metadata: dict,
    this_idx: str,
    form_json_page: dict,
    page_index: dict,
    parent_hierarchy_level: str,
    pages_to_do: list,
    place_in_siblings_list: int,
    index_of_printed_headers: dict,
    is_form_heading: bool = False,
    lang: str = "en",
):
    """Generates the heading text and hierarchical number for this page and it's children

    Args:
        page (dict): This page from the metadata
        form_metadata (dict): Full metadata for this form
        this_idx (str): The heading number for the page that came before this one
        form_json_page (dict): Full json for this page from the form json
        page_index (dict): Hierarchy levels by page path
        parent_hierarchy_level (str): Hierarchy level for the page that came before this one
        pages_to_do (list): List of pages left to add to the results
        place_in_siblings_list (int): Where this page is in a list of siblings, so multiple sub-pages
            are numbered correctly
        index_of_printed_headers (dict): Results are stored here as a dict:
            ```
            index_of_printed_headers[page_path] = {
                "heading_number": Number for this page eg. 1.2.3 - str,
                "is_form_heading": bool,
                "title": title text to display - str,
            }
            ```
        is_form_heading (bool, optional): Whether or not this is the heading for the entire form. Defaults to False.
    """
    page_path = page["path"]
    # If we've already done this page, don't do it again
    if page_path not in pages_to_do:
        return

    title = strip_leading_numbers(form_json_page["title"])

    level_in_hrch = page_index[page_path]
    hierarchy_difference = level_in_hrch - parent_hierarchy_level

    # If we are going up a level in the hierarchy, and this isn't the last branch
    # that goes there, don't do it yet
    all_siblings = set(prev for prev in page["direct_next_of_direct_previous"] if prev != page_path)
    if pages_to_do.intersection(all_siblings) and hierarchy_difference < 0:
        return

    if pages_to_do.intersection(page["all_direct_previous"]) and hierarchy_difference < 0:
        return

    # Work out the heading number for this page
    base_heading_number = this_idx
    if not is_form_heading:
        if hierarchy_difference < 0:
            # go back a level
            base_heading_number = remove_lowest_in_hierarchy(base_heading_number)
        elif hierarchy_difference > 0:
            # increase level
            base_heading_number = f"{this_idx}.{place_in_siblings_list}"

    new_heading_number = increment_lowest_in_hierarchy(base_heading_number)

    index_of_printed_headers[page_path] = {
        "heading_number": new_heading_number,
        "is_form_heading": is_form_heading,
        "title": title,
    }
    # Make sure we don't do this page again
    pages_to_do.remove(page_path)

    # Go through and do the same for all the pages after this one
    sibling_tracker = 0
    for next_page_path in page["next_paths"]:
        next_page = next(p for p in form_metadata["all_pages"] if p["path"] == next_page_path)
        next_form_json_page = next(p for p in form_metadata["full_json"]["pages"] if p["path"] == next_page_path)
        generate_print_headings_for_page(
            page=next_page,
            form_metadata=form_metadata,
            this_idx=new_heading_number,
            form_json_page=next_form_json_page,
            page_index=page_index,
            parent_hierarchy_level=level_in_hrch,
            pages_to_do=pages_to_do,
            is_form_heading=False,
            place_in_siblings_list=sibling_tracker,
            index_of_printed_headers=index_of_printed_headers,
            lang=lang,
        )
        sibling_tracker += 1


def generate_print_data_for_form(section_idx: int, form_metadata: dict, form_idx: int, lang: str = "en"):
    """Uses `generate_print_headings_for_page()` and `build_components_from_page()`
    to gather everything that needs to be printed for this form


    Args:
        section_idx (int): Index of this section (above form level)
        form_metadata (dict): Metadata for this form
        form_idx (int): Index of this form within the section

    Returns:
        dict : Keys are page paths, values are what to print:
        ```
        "/intro-to-form": {
            "heading_number": Number for this page eg. 1.2.3 - str,
            "is_form_heading": bool,
            "title": title text to display - str,
            "components": [] (generated by `build_components_from_page`)
        }
        ```
    """
    # Create a list of all the required pages for printing
    pages_to_do = set(p["path"] for p in form_metadata["all_pages"] if p["path"] != "/summary")
    start_page_path = form_metadata["start_page"]
    index = form_metadata["index"]
    start_page_metadata = next(p for p in form_metadata["all_pages"] if p["path"] == start_page_path)
    start_page_json = next(p for p in form_metadata["full_json"]["pages"] if p["path"] == start_page_path)

    current_hierarchy_level = 0
    index_of_printed_headers = {}
    # Generate the headings for the start page - this function is then recursive so goes down the
    # entire tree in the form
    generate_print_headings_for_page(
        start_page_metadata,
        form_metadata,
        this_idx=f"{section_idx}.{form_idx}",
        form_json_page=start_page_json,
        page_index=index,
        parent_hierarchy_level=current_hierarchy_level,
        pages_to_do=pages_to_do,
        is_form_heading=True,
        place_in_siblings_list=0,
        index_of_printed_headers=index_of_printed_headers,  # This is updated with the results
        lang=lang,
    )

    # For each page, generate the list of components to print
    for page_path in index_of_printed_headers.keys():
        full_json_page = next(p for p in form_metadata["full_json"]["pages"] if p["path"] == page_path)
        component_display = build_components_from_page(
            full_page_json=full_json_page,
            include_html_components=(not determine_if_just_html_page(full_json_page["components"])),
            form_lists=form_metadata["full_json"]["lists"],
            form_conditions=form_metadata["full_json"]["conditions"],
            index_of_printed_headers=index_of_printed_headers,
            lang=lang,
        )
        index_of_printed_headers[page_path]["components"] = component_display
    return index_of_printed_headers


form_json_to_assessment_display_types = {
    "numberfield": "integer",
    "textfield": "text",
    "yesnofield": "text",
    "freetextfield": "free_text",
    "checkboxesfield": "list",
    "multiinputfield": "table",
    "multilinetextfield": "text",
    "clientsidefileuploadfield": "s3bucketPath",
    "radiosfield": "text",
    "emailaddressfield": "text",
    "telephonenumberfield": "text",
    "ukaddressfield": "address",
}


def generate_assessment_display_info_for_fields(form_json: dict, form_name: str) -> list:
    """Generates a list of the fields and their display types for use in assessment config

    Args:
        form_json (dict): Form json for this form
        form_name (str): Name of the form

    Returns:
        list: List of dictionaries, keys are form names, values are lists of the fields in that form
    """
    # TODO write tests
    results = []
    for page in form_json["pages"]:
        for component in page["components"]:
            question = component.get("title", None)
            if component["type"].lower() == "multiinputfield":
                question = [page["title"]]
                child_fields = {}
                for field in component["children"]:
                    child_fields[field["name"]] = {
                        "column_title": field["title"],
                        "type": field["type"],
                    }
                question.append(child_fields)

            results.append(
                {
                    "field_id": component["name"],
                    "form_name": form_name,
                    "field_type": component["type"],
                    "presentation_type": form_json_to_assessment_display_types.get(component["type"].lower(), None),
                    "question": question,
                }
            )
    return results


def generate_print_data_for_sections(
    sections: list[dict],
    lang: str,
    include_assessment_field_details: bool = False,
) -> dict:
    """Creates a dictionary for this section containing the data to print for every form in each section

    Args:
        sections (list[Section]): List of sections to generate print data
        path_to_form_jsons (str): Absolute path to the form jsons directory
            (eg. /dev/form-builder/fsd_config/form-jsons/cof_r2w3/en/)
        lang (str): Language string: `en` or `cy`
        include_assessment_field_details (bool): Whether to include field details for display in assessment

    Returns:
        dict: Containing everything to print for each form
        ```
            anchor-id-for-section: = {
                "title_text": str Text to display for section title,
                "form_print_data": {} All the data for each form in this section, as generated
                    by `generate_print_data_for_form`,
                "assessment_display_info": {} Field details for display in assessment

            }
        ```
    """
    section_map = {}
    assessment_display_info = {}

    section_idx = 1
    for section in sections:
        anchor, text = build_section_header(section["section_title"], lang=lang)
        form_print_data = {}
        form_idx = 0
        for child_form in section["forms"]:
            form_data = child_form["form_data"]
            form_metadata = generate_metadata(form_data)
            form_index = {}

            first_page = next(p for p in form_metadata["all_pages"] if p["path"] == form_metadata["start_page"])

            # Work out what hierarchy level each page is on
            build_hierarchy_levels_for_page(
                page=first_page,
                results=form_index,
                idx=1,
                all_pages=form_metadata["all_pages"],
                start_page=True,
            )
            form_metadata["index"] = form_index
            form_metadata["full_json"] = form_data

            # Grab the print data for this form and add it to the results
            form_print_data.update(
                generate_print_data_for_form(
                    section_idx=section_idx,
                    form_metadata=form_metadata,
                    form_idx=form_idx,
                    lang=lang,
                )
            )

            # if include_assessment_field_details:
            #     assessment_field_details = generate_assessment_display_info_for_fields(
            #         form_json=form_data, form_name=form_name
            #     )
            #     assessment_display_info[form_name] = assessment_field_details

            form_idx += 1
        section_map[anchor] = {
            "title_text": text,
            "form_print_data": form_print_data,
            "assessment_display_info": assessment_display_info,
        }
        section_idx += 1
    return section_map
