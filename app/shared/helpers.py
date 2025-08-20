from dataclasses import asdict, is_dataclass

from flask import flash, render_template


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


def human_to_kebab_case(string: str) -> str | None:
    return string.replace(" ", "-").strip().lower() if string else None


def human_to_snake_case(string: str) -> str | None:
    return string.replace(" ", "_").strip().lower() if string else None
