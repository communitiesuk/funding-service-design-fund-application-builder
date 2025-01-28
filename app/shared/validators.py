import re

from wtforms.validators import ValidationError


class NoSpacesBetweenLetters:
    """
    validate is there empty spaces between letters
    """

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        # Regular expression to check for spaces between letters
        if not field.data:
            return
        if re.search(r"\b\w+\s+\w+\b", field.data):  # Matches sequences with spaces in between
            raise ValidationError(self.message)


class FlexibleUrl:
    """
    validate is there empty spaces between letters
    """

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        """
        Validates URLs allowing:
        - Optional scheme (http://, https://)
        - Domain names with multiple subdomains
        - Optional paths, query parameters
        - Common TLDs
        - No scheme required
        """
        if not field.data:
            return

        pattern = (
            # Optional scheme
            r"^(?:(?:http|https)://)?"
            # Domain with optional subdomains
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63})"
            # Optional port
            r"(?::\d+)?"
            # Optional path
            r"(?:/[^/\s]*)*"
            # Optional query string
            r"(?:\?[^\s]*)?"
            # Optional fragment
            r"(?:#[^\s]*)?$"
        )

        if not re.match(pattern, field.data, re.IGNORECASE):
            raise ValidationError(self.message)


class WelshDataRequired:
    """
    validate is there empty spaces between letters
    """

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        # Check if Welsh is available and name_cy is required
        if form.welsh_available.data and not (field.data and field.data.strip()):
            raise ValidationError(self.message)
