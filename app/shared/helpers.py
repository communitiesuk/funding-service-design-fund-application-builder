import math
import re
from dataclasses import asdict, is_dataclass
from typing import List

from flask import request

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
        rows_per_page: int = 2,
        page_description: str = '',
        summary_text: str = '',
        summary_description: str = '',
        button_text: str = '',
        table_rows: List[dict] = None,
        table_caption: str = '',
        table_heading: List[dict] = None,
):
    """
    Handles the rendering of a paginated table with various optional metadata for page layout.

    This function is designed to take a list of table rows, paginate them based on the specified
    number of rows per page, and return a dictionary with the necessary information to render a
    generic table page, including pagination links and optional text fields for headers,
    descriptions, and buttons.

    Args:
        page_heading (str): The heading for the page. Default to an empty string.
        rows_per_page (int, optional): The number of rows to display per page. Default to 2.
        page_description (str, optional): The description to display on the page. Default to an empty string.
        summary_text (str, optional): A summary or introductory text for the page. Default to an empty string.
        summary_description (str, optional): A description of the summary text. Default to an empty string.
        button_text (str, optional): The text for a button on the page. Default to an empty string.
        table_rows (list, optional): A list of table rows to be displayed on the page. Defaults to None.
        table_caption (str, optional): The caption for the table. Default to an empty string.
        table_heading (str, optional): The heading of the table, typically the column headers. Defaults to None.

    Returns:
        dict: A dictionary containing all the necessary data for rendering the page, including:
            - "page_heading": The heading of the page.
            - "page_description": The description of the page.
            - "detail": A dictionary containing "summary_text" and "text" (summary_description).
            - "button_text": The button text for the page.
            - "table": A dictionary with keys "caption", "head", and "rows" (the paginated rows).
            - "pagination": A dictionary containing pagination metadata (previous, next, and page numbers).
    """
    current_page = 1
    if "page" in request.args:  # Check if 'page' is in the query string
        current_page = int(request.args.get("page", 1))  # Get 'page' or default to 1

    # Validate that page_heading is mandatory
    if not page_heading:
        raise ValueError("The page heading parameter is mandatory and cannot be empty.")

    # If summary_text is provided, summary_description must also be provided
    if summary_text and not summary_description:
        raise ValueError("If summary text is provided, Summary description must also be provided.")

    # If summary_text is provided, summary_description must also be provided
    if summary_description and not summary_text:
        raise ValueError("If summary description is provided, Summary text must also be provided.")

    # If table_rows is provided, table_heading must also be provided
    if table_rows and not table_heading:
        raise ValueError("If table rows are provided, Table headers must also be provided.")

    if table_rows is None:
        table_rows = []
    if table_heading is None:
        table_heading = []
    # Paginate the data
    total_pages = len(table_rows)
    number_of_pages = math.ceil(total_pages / rows_per_page)
    start_index = (current_page - 1) * rows_per_page
    end_index = start_index + rows_per_page
    paginated_rows = table_rows[start_index:end_index]
    # Pagination metadata
    pagination = {
        "items": [
            {
                "number": i,
                "href": f"?page={i}",
                **({"current": True} if i == current_page else {})  # Add "current" only if i == current_page
            }
            for i in range(1, max(number_of_pages, 1))
        ],
        **({"previous": {"href": f"?page={current_page - 1}"}} if current_page > 1 else {}),
        **({"next": {"href": f"?page={current_page + 1}"}} if current_page < number_of_pages else {})
    }
    genericDataSet = {
        "page_heading": page_heading,
        "page_description": page_description,
        "detail": {
            "summary_text": summary_text,
            "text": summary_description,
        },
        "button_text": button_text,
        "table": {
            "caption": table_caption,
            "head": table_heading,
            "rows": paginated_rows
        },
        "pagination": pagination
    }
    return genericDataSet
