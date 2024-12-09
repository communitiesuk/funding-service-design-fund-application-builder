import pytest
from wtforms.validators import ValidationError

from app.blueprints.fund_builder.forms.round import validate_flexible_url


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
        ("http://google.com", True),  # NOSONAR
        ("https://google.com", True),
        ("https://www.google.com", True),
        # URLs with paths
        ("google.com/path", True),
        ("google.com/path/to/resource", True),
        ("google.com/path?query=value", True),
        ("google.com/path#fragment", True),
        # URLs with ports
        ("google.com:8080", True),
        ("http://google.com:8080", True),  # NOSONAR
        # Complex URLs
        ("https://sub.domain.google.co.uk:8080/path/to/resource?query=value#fragment", True),
        # Invalid URLs
        ("", True),  # Empty string is allowed by the validator
        ("not_a_url", False),
        ("http://", False),  # NOSONAR
        ("http://.com", False),  # NOSONAR
        (".com", False),
        ("http://google", False),  # Missing TLD  # NOSONAR
        ("http://google.", False),  # NOSONAR
        ("http://-google.com", False),  # Invalid domain start  # NOSONAR
        ("http://google-.com", False),  # Invalid domain end  # NOSONAR
        ("http://goo gle.com", False),  # Contains space  # NOSONAR
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