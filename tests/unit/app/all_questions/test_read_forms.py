import pytest

from app.all_questions.read_forms import strip_leading_numbers


@pytest.mark.parametrize(
    "input,expected_output",
    [
        ("1. Section", "Section"),
        ("1.1.Section", "Section"),
        ("Section 1.1", "Section 1.1"),
        ("1 Sect1on 1", "Sect1on 1"),
    ],
)
def test_strip_leading_numbers(input: str, expected_output: str):
    assert strip_leading_numbers(input) == expected_output
