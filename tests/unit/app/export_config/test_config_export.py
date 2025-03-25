import json
import secrets
import string
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from app.blueprints.application.routes import create_export_zip
from app.export_config.generate_fund_round_form_jsons import (
    generate_form_jsons_for_round,
)
from app.export_config.generate_fund_round_html import (
    frontend_html_prefix,
    frontend_html_suffix,
    generate_all_round_html,
)
from app.export_config.helpers import validate_json


def test_generate_form_jsons_for_round_valid_input(seed_dynamic_data, temp_output_dir):
    # Setup: Prepare valid input parameters
    round_id = seed_dynamic_data["rounds"][0].round_id
    round_short_name = seed_dynamic_data["rounds"][0].short_name
    form_publish_name = seed_dynamic_data["forms"][0].runner_publish_name

    # Execute: Call the function with valid inputs
    generate_form_jsons_for_round(round_id)
    # Assert: Check if the directory structure and files are created as expected
    expected_files = [
        {
            "path": temp_output_dir / round_short_name / "form_runner" / f"{form_publish_name}.json",
            "expected_output": {
                "startPage": "/intro-about-your-organisation",
                "pages": [
                    {
                        "path": "/organisation-name",
                        "title": "Organisation Name",
                        "components": [
                            {
                                "options": {"hideTitle": False, "classes": ""},
                                "type": "TextField",
                                "title": "What is your organisation's name?",
                                "hint": "This must match the registered legal organisation name",
                                "schema": {},
                                "name": "organisation_name",
                            },
                            {
                                "options": {"hideTitle": False, "classes": ""},
                                "type": "RadiosField",
                                "title": "How is your organisation classified?",
                                "hint": "",
                                "schema": {},
                                "name": "organisation_classification",
                                "list": "classifications_list",
                                "values": {"type": "listRef"},
                            },
                        ],
                        "next": [{"path": "/summary"}],
                    },
                    {
                        "path": "/intro-about-your-organisation",
                        "title": "About your organisation",
                        "components": [
                            {
                                "name": "start-page-content",
                                "options": {},
                                "type": "Html",
                                "content": '<p class="govuk-body"></p><p class="govuk-body">'
                                "We will ask you about:</p> <ul><li>Organisation Name</li></ul>",
                                "schema": {},
                            }
                        ],
                        "next": [{"path": "/organisation-name"}],
                        "controller": "./pages/start.js",
                    },
                    {
                        "path": "/summary",
                        "title": "Check your answers",
                        "components": [],
                        "next": [],
                        "section": "uLwBuz",
                        "controller": "./pages/summary.js",
                    },
                ],
                "lists": [
                    {
                        "type": "string",
                        "items": [
                            {"text": "Charity", "value": "charity"},
                            {"text": "Public Limited Company", "value": "plc"},
                        ],
                        "name": "classifications_list",
                        "title": None,
                    }
                ],
                "conditions": [],
                "sections": [],
                "outputs": [],
                "skipSummary": False,
                "name": "Apply for funding to improve testing",
            },
        }
    ]
    for expected_file in expected_files:
        path = expected_file["path"]
        assert path.exists(), f"Expected file {path} does not exist."

    with open(expected_file["path"], "r") as file:
        data = json.load(file)
        for page in data["pages"]:
            for component in page["components"]:
                component.pop("metadata", None)
        assert data == expected_file["expected_output"]


def test_generate_form_jsons_for_round_invalid_input(seed_dynamic_data):
    # Setup: Prepare invalid input parameters
    round_id = None
    # Execute and Assert: Ensure the function raises an exception for invalid inputs
    with pytest.raises(ValueError):
        generate_form_jsons_for_round(round_id)


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


test_json_schema = {
    "type": "object",
    "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
    "required": ["name", "age"],
}


def test_valid_data_validate_json():
    # Data that matches the schema
    data = {"name": "John Doe", "age": 30}
    result = validate_json(data, test_json_schema)
    assert result, "The data should be valid according to the schema"


@pytest.mark.parametrize(
    "data",
    [
        ({"age": 30}),  # Missing 'name'
        ({"name": 123}),  # 'name' should be a string
        ({"name": ""}),  # 'name' is empty
        ({}),  # Empty object
        ({"name": "John Doe", "extra_field": "not allowed"}),  # Extra field not defined in schema
        # Add more invalid cases as needed
    ],
)
def test_invalid_data_validate_json(data):
    result = validate_json(data, test_json_schema)
    assert not result, "The data should be invalid according to the schema"


def test_create_export_zip(temp_output_dir):
    test_data_path = Path("tests") / "test_data"
    random_post_fix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    output = create_export_zip(
        directory_to_zip=test_data_path, zip_file_name="test_zip", random_post_fix=random_post_fix
    )
    assert output
    output_path = Path(output)
    assert output_path.exists()


def _normalize_html(html):
    """Parses and normalizes HTML using BeautifulSoup to avoid formatting differences."""
    return BeautifulSoup(html, "html.parser").prettify()
