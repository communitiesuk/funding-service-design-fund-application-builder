import re
from dataclasses import asdict, is_dataclass

from flask import flash, render_template
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


def flash_message(
    message: str,
    href: str = None,
    href_display_name: str = None,
    next_href: str = None,
    next_href_display_name: str = None,
):
    """
    Displays custom flash message.
    This function renders an HTML template for a flash message and displays it using Flask's `flash` function.
    Args:
        message (str): The main message to be displayed in the flash notification.
        href (str): The URL for the primary hyperlink.
        href_display_name (str): The display text for the primary hyperlink.

        next_href (str, optional): The URL for the secondary hyperlink.
        next_href_display_name (str, optional): The display text for the secondary hyperlink.

    Example:
        ```python
        flash_message(
            message="Your changes were saved successfully",
            href="/dashboard",
            href_display_name="Go to Dashboard",
            next_href="/settings",
            next_href_display_name="Edit Settings"
        )
        ```
    """
    flash(render_template("partials/flash_template.html", **locals()))
