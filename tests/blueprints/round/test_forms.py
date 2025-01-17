from unittest.mock import MagicMock

import pytest
from wtforms.validators import ValidationError

from app.blueprints.round.forms import validate_flexible_url, validate_json_field


class MockField:
    def __init__(self, data):
        self.data = data


@pytest.mark.parametrize(
    "url,should_pass",
    [
        # Basic URLs
        ("google.com", True),
        ("www.google.com", True),
        ("sub.google.com", True),
        ("google.co.uk", True),
        # URLs with schemes
        ("http://google.com", True),
        ("https://google.com", True),
        ("https://www.google.com", True),
        # URLs with paths
        ("google.com/path", True),
        ("google.com/path/to/resource", True),
        ("google.com/path?query=value", True),
        ("google.com/path#fragment", True),
        # URLs with ports
        ("google.com:8080", True),
        ("http://google.com:8080", True),
        # Complex URLs
        ("https://sub.domain.google.co.uk:8080/path/to/resource?query=value#fragment", True),
        # Invalid URLs
        ("", True),  # Empty string is allowed by the validator
        ("not_a_url", False),
        ("http://", False),
        ("http://.com", False),
        (".com", False),
        ("http://google", False),  # Missing TLD
        ("http://google.", False),
        ("http://-google.com", False),  # Invalid domain start
        ("http://google-.com", False),  # Invalid domain end
        ("http://goo gle.com", False),  # Contains space
        ("javascript:alert(1)", False),  # JavaScript URL
        ("file:///etc/passwd", False),  # File URL
    ],
)
def test_validate_flexible_url(url, should_pass):
    field = MockField(url)
    mock_form = None  # Not needed for this validator

    if should_pass:
        try:
            validate_flexible_url(mock_form, field)
        except ValidationError:
            pytest.fail(f"URL '{url}' should have passed validation but failed")
    else:
        with pytest.raises(ValidationError):
            validate_flexible_url(mock_form, field)


def test_validate_flexible_url_none_value():
    """Test that None value is handled gracefully"""
    field = MockField(None)
    validate_flexible_url(None, field)  # Should not raise any exception


@pytest.mark.parametrize("input_json_string", [(None), (""), ("{}"), (""), ("{}"), ('{"1":"2"}')])
def test_validate_json_input_valid(input_json_string):
    field = MagicMock()
    field.data = input_json_string
    validate_json_field(None, field)


@pytest.mark.parametrize(
    "input_json_string, exp_error_msg",
    [
        ('{"1":', "Expecting value: line 1 column 6 (char 5)]"),
        ('{"1":"quotes not closed}', "Unterminated string starting at: line 1 column 6 (char 5)"),
    ],
)
def test_validate_json_input_invalid(input_json_string, exp_error_msg):
    field = MagicMock()
    field.data = input_json_string
    with pytest.raises(ValidationError) as error:
        validate_json_field(None, field)
    assert exp_error_msg in str(error)
