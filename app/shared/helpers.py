from dataclasses import asdict, is_dataclass

from flask import flash, render_template

from app.db.models import Page
from flask_sqlalchemy.pagination import Pagination


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


def pagination_convertor(pagination: Pagination):
    """
    convert a backend-paginated object into gov uk pagination

    Args:
        pagination (dict): backend-paginated object and convert into gov uk pagination.
    """

    if pagination.pages <= 1:
        return None

    pagination_json = {
        **({"previous": {"href": f"?page={pagination.prev_num}"}} if pagination.has_prev else {}),
        **({"next": {"href": f"?page={pagination.next_num}"}} if pagination.has_next else {}),
        "items": []
    }

    # Helper function to add page number or ellipsis
    def add_page(i, current_page):
        return {"number": i, "href": f"?page={i}", "current": i == current_page}

    items = []
    # Add pages before the current page
    if pagination.page > 3:
        #  More than 3 pages left to the current then add ellipsis with the first page
        items.extend([add_page(1, pagination.page), {"ellipsis": True}])

    # Filling the left-hand side with items after current and ignore ellipsis range
    start = max(1, pagination.page - 1)
    for i in range(start, pagination.page):
        items.append(add_page(i, pagination.page))

    # Add the current page
    items.append(add_page(pagination.page, pagination.page))

    # Add pages after the current page
    if pagination.page < pagination.pages - 2:
        # Add ellipsis if there are more than pages after current pages after remove last one and once after the current
        items.append(add_page(pagination.page + 1, pagination.page))
        items.append({"ellipsis": True})
        items.append(add_page(pagination.pages, pagination.page))
    else:
        # adding all the items if there is no ellipsis
        items.extend(add_page(i, pagination.page) for i in range(pagination.page + 1, pagination.pages + 1))

    # Assign the items to the pagination JSON
    pagination_json["items"] = items
    return pagination_json
