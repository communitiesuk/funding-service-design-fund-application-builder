import re
from dataclasses import asdict
from dataclasses import is_dataclass

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
    errors = form.errors
    error = None
    if errors:
        errorsList = []
        for field, errors in errors.items():
            field_name = getattr(form, field).label.text
            if isinstance(errors, list):
                errorsList.extend([{"text": f"{field_name}: {err}", "href": f"#{field}"} for err in errors])
            elif isinstance(errors, dict):
                # Check if any of the datetime fields have errors
                if any(len(errors.get(key, "")) > 0 for key in ["day", "month", "years", "hour", "minute"]):
                    errorsList.append({"text": f"{field_name}: Enter valid datetime", "href": f"#{field}"})
        if errorsList:
            error = {"titleText": "There is a problem", "errorList": errorsList}
    return error


# Custom validator to check for spaces between letters
def no_spaces_between_letters(form, field):
    # Regular expression to check for spaces between letters
    if not field.data:
        return
    if re.search(r"\b\w+\s+\w+\b", field.data):  # Matches sequences with spaces in between
        raise ValidationError("Spaces between letters are not allowed.")
