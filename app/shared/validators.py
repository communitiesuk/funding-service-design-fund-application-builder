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
