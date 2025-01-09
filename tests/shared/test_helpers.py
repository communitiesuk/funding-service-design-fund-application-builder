import pytest

from app.shared.helpers import is_safe_url


@pytest.mark.parametrize(
    "url,expected",
    [
        # Valid paths
        ("/dashboard", True),
        ("/funds/view", True),
        ("/funds/123/edit", True),
        ("/some-path/with-hyphens", True),
        ("/path_with_underscore", True),
        ("/", True),
        # Invalid paths
        (None, False),
        ("", False),
        ("dashboard", False),  # missing leading slash
        ("//evil.com", False),
        ("\\evil.com", False),
        ("/\\evil.com", False),
        ("/%2F%2Fevil.com", False),
        ("http://evil.com", False),
        ("/path with spaces", False),
        ("/path.with.dots", False),
        ("/path@with@special@chars", False),
        ("/path?with=query", False),
        ("/path#with-fragment", False),
        ("/../etc/passwd", False),  # directory traversal attempt
    ],
)
def test_is_safe_url(url, expected):
    assert is_safe_url(url) == expected
