import re
from dataclasses import asdict, is_dataclass

from wtforms.validators import ValidationError

from app.db.models import Page


def convert_to_dict(obj):
    if is_dataclass(obj):
        return asdict(obj)
    elif isinstance(obj, list):
        return [asdict(item) if is_dataclass(item) else item for item in obj]
    else:
        return obj


def find_enum(enum_class, value):
    for enum in enum_class:
        if enum.value == value:
            return enum
    return None


def get_all_pages_in_parent_form(db, page_id):
    # Get the form_id from page_id
    page = db.session.query(Page).filter(Page.page_id == page_id).first()

    if page is None:
        raise ValueError(f"No page found with page_id: {page_id}")

    form_id = page.form_id

    # Get all page ids belonging to the form
    page_ids = db.session.query(Page.page_id).filter(Page.form_id == form_id).all()

    # Extract page_ids from the result
    page_ids = [p.page_id for p in page_ids]

    return page_ids


# This formatter will read all the errors and then convert them to the required format to support error-summary display
def error_formatter(form):
    errors_list = []
    for field, error_messages in form.errors.items():
        field_name = getattr(form, field).label.text
        if isinstance(error_messages, list):
            errors_list.extend({"text": f"{field_name}: {err}", "href": f"#{field}"} for err in error_messages)
        elif isinstance(error_messages, dict) and any(
            error_messages.get(k) for k in ["day", "month", "years", "hour", "minute"]
        ):
            errors_list.append({"text": f"{field_name}: Enter valid datetime", "href": f"#{field}"})
    if errors_list:
        return {"titleText": "There is a problem", "errorList": errors_list}
    return None


# Custom validator to check for spaces between letters
def no_spaces_between_letters(form, field):
    # Regular expression to check for spaces between letters
    if not field.data:
        return
    if re.search(r"\b\w+\s+\w+\b", field.data):  # Matches sequences with spaces in between
        raise ValidationError("Spaces between letters are not allowed.")


def all_funds_as_govuk_select_items(all_funds: list) -> list:
    """
    Reformats a list of funds into a list of display/value items that can be passed to a govUk select macro
    in the html
    """
    return [{"text": f"{f.short_name} - {f.name_json['en']}", "value": str(f.fund_id)} for f in all_funds]


def handle_generic_table_page(
    page_heading: str,
    page_description: str,
    detail_text: str,
    detail_description: str,
    button_text: str,
    button_url: str,
    table_header: list[dict],
    table_rows: list[dict],
):
    """
    Handles the rendering of a paginated table with various optional metadata for page layout.

    This function is designed to take a list of table rows, paginate them based on the specified
    number of rows per page, and return a dictionary with the necessary information to render a
    generic table page, including pagination links and optional text fields for headers,
    descriptions, and buttons.

    Args:
        page_heading (str): The heading for the page.
        page_description (str): The description to display on the page.
        detail_text (str): A detail title or introductory text for the page.
        detail_description (str): A detail description of the detail title.
        button_text (str): The text for a button on the page.
        button_url (str): Button URL for the page.
        table_header (list): The heading of the table, typically the column headers.
        table_rows (list): A list of table rows to be displayed on the page.

    Returns:
        dict: A dictionary containing all the necessary data for rendering the page, including:
            - "page_heading": The heading of the page.
            - "page_description": The description of the page.
            - "detail": A dictionary containing "summary_text" and "text" (summary_description).
            - "button_text": The button text for the page.
            - "table": A dictionary with keys "caption", "head", and "rows" (the paginated rows).
    """

    genericDataSet = {
        "page_heading": page_heading,
        "page_description": page_description,
        "detail": {
            "detail_text": detail_text,
            "detail_description": detail_description,
        },
        "button": {
            "button_text": button_text,
            "button_url": button_url,
        },
        "table": {"table_header": table_header, "table_rows": table_rows},
    }
    return genericDataSet
