import pytest
from bs4 import BeautifulSoup

from app.export_config.generate_fund_round_html import (
    frontend_html_prefix,
    frontend_html_suffix,
    generate_all_round_html,
)


def test_generate_fund_round_html(seed_dynamic_data, temp_output_dir):
    # Setup: Prepare valid input parameters
    round_id = seed_dynamic_data["rounds"][0].round_id
    round_short_name = seed_dynamic_data["rounds"][0].short_name
    fund_short_name = seed_dynamic_data["funds"][0].short_name
    # Execute: Call the function with valid inputs
    generate_all_round_html(round_id)
    # Assert: Check if the directory structure and files are created as expected
    expected_files = [
        {
            "path": temp_output_dir
            / round_short_name
            / "html"
            / f"{fund_short_name.casefold()}_{round_short_name.casefold()}_all_questions_en.html",
            "expected_output": frontend_html_prefix
            + '<div class="govuk-!-margin-bottom-8">\n  <h2 class="govuk-heading-m">Table of contents</h2>\n  <ol class="govuk-list govuk-list--number">\n    <li><a class="govuk-link" href="#organisation-information">Organisation Information</a></li>\n  </ol>\n  <hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible" />\n  <h2 class="govuk-heading-l" id="organisation-information">1. Organisation Information</h2>\n  <h3 class="govuk-heading-m">About your organisation</h3>\n  <hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible" />\n  <h4 class="govuk-heading-s">Organisation Name</h4>\n  <div class="govuk-body">\n    <p class="govuk-body">What is your organisation\'s name?</p>\n    <p class="govuk-body">This must match the registered legal organisation name</p>\n  </div>\n  <div class="govuk-body">\n    <p class="govuk-body">How is your organisation classified?</p>\n    <ul class="govuk-list govuk-list--bullet">\n      <li>Charity</li>\n      <li>Public Limited Company</li>\n    </ul>\n  </div>\n  <hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible" />\n</div>'  # noqa: E501
            + frontend_html_suffix,
        }
    ]
    for expected_file in expected_files:
        path = expected_file["path"]
        assert path.exists(), f"Expected file {path} does not exist."

    with open(expected_file["path"], "r") as file:
        data = file.read()
        assert _normalize_html(data) == _normalize_html(expected_file["expected_output"]), "HTML outputs do not match"


def test_generate_fund_round_html_invalid_input(seed_dynamic_data):
    # Setup: Prepare invalid input parameters
    round_id = None
    # Execute and Assert: Ensure the function raises an exception for invalid inputs
    with pytest.raises(ValueError):
        generate_all_round_html(round_id)


def _normalize_html(html):
    """Parses and normalizes HTML using BeautifulSoup to avoid formatting differences."""
    return BeautifulSoup(html, "html.parser").prettify()
