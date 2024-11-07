import ast
import json
from pathlib import Path

import pytest

from app.blueprints.fund_builder.routes import create_export_zip
from app.export_config.generate_fund_round_config import generate_config_for_round
from app.export_config.generate_fund_round_form_jsons import (
    generate_form_jsons_for_round,
)
from app.export_config.generate_fund_round_html import frontend_html_prefix
from app.export_config.generate_fund_round_html import frontend_html_suffix
from app.export_config.generate_fund_round_html import generate_all_round_html
from app.export_config.helpers import validate_json


def read_data_from_output_file(file):
    content = file.read()
    # Safely evaluate the Python literal structure
    # only evaluates literals and not arbitrary code
    content = content.split("LOADER_CONFIG=")[1]
    data = ast.literal_eval(content)
    return data


def test_generate_config_for_round_valid_input(seed_dynamic_data, monkeypatch, temp_output_dir):
    # Setup: Prepare valid input parameters
    fund_short_name = seed_dynamic_data["funds"][0].short_name
    round_id = seed_dynamic_data["rounds"][0].round_id
    round_short_name = seed_dynamic_data["rounds"][0].short_name
    mock_round_base_paths = {round_short_name: 99}

    # Use monkeypatch to temporarily replace ROUND_BASE_PATHS
    import app.export_config.generate_fund_round_config as generate_fund_round_config

    monkeypatch.setattr(generate_fund_round_config, "ROUND_BASE_PATHS", mock_round_base_paths)
    # Execute: Call the function with valid inputs
    result = generate_config_for_round(round_id)
    # Simply writes the files to the output directory so no result is given directly
    assert result is None
    # Assert: Check if the directory structure and files are created as expected
    expected_files = [
        {
            "path": temp_output_dir / round_short_name / "fund_store" / "round_config.py",
            "expected_output": {
                "sections_config": [
                    {
                        "section_name": {"en": "1. Organisation Information", "cy": ""},
                        "requires_feedback": None,
                    },
                    {
                        "section_name": {"en": "1.1 About your organisation", "cy": ""},
                        "form_name_json": {"en": "about-your-org", "cy": ""},
                    },
                ],
                "fund_config": {
                    "short_name": fund_short_name,
                    "welsh_available": False,
                    "owner_organisation_name": "None",
                    "owner_organisation_shortname": "None",
                    "owner_organisation_logo_uri": "None",
                    "name_json": {"en": "Unit Test Fund 1"},
                    "title_json": {"en": "funding to improve testing"},
                    "description_json": {"en": "A £10m fund to improve testing across the devolved nations."},
                    "funding_type": "COMPETITIVE",
                },
                "round_config": {
                    "short_name": round_short_name,
                    "application_reminder_sent": False,
                    "prospectus": "http://www.google.com",
                    "privacy_notice": "http://www.google.com",
                    "reference_contact_page_over_email": False,
                    "contact_email": "test@test.com",
                    "contact_phone": "0123334444",
                    "contact_textphone": "0123334444",
                    "support_times": "9am to 5pm",
                    "support_days": "Monday to Friday",
                    "instructions_json": None,
                    "feedback_link": "http://www.google.com",
                    "project_name_field_id": "12312312312",
                    "application_guidance_json": None,
                    "guidance_url": "http://www.google.com",
                    "all_uploaded_documents_section_available": False,
                    "application_fields_download_available": False,
                    "display_logo_on_pdf_exports": False,
                    "mark_as_complete_enabled": False,
                    "is_expression_of_interest": False,
                    "eoi_decision_schema": {"en": {"valid": True}, "cy": {"valid": False}},
                    "feedback_survey_config": {"has_survey": False},
                    "eligibility_config": {"has_eligibility": False},
                    "title_json": {"en": "round the first"},
                    "contact_us_banner_json": None,
                },
            },
        },
    ]
    for expected_file in expected_files:
        path = expected_file["path"]
        assert path.exists(), f"Expected file {path} does not exist."

        with open(expected_file["path"], "r") as file:
            data = read_data_from_output_file(file=file)

            if expected_file["expected_output"].get("fund_config", None):
                # remove keys that can't be accurately compared
                keys_to_remove = ["base_path"]
                keys_to_remove_fund_config = ["id"]
                keys_to_remove_round_config = [
                    "id",
                    "fund_id",
                    "reminder_date",
                    "assessment_start",
                    "assessment_deadline",
                    "deadline",
                    "opens",
                ]
                keys_to_remove_section_config = ["tree_path"]
                data = {k: v for k, v in data.items() if k not in keys_to_remove}
                data["fund_config"] = {
                    k: v for k, v in data["fund_config"].items() if k not in keys_to_remove_fund_config
                }
                data["round_config"] = {
                    k: v for k, v in data["round_config"].items() if k not in keys_to_remove_round_config
                }
                data["sections_config"] = [
                    {k: v for k, v in section.items() if k not in keys_to_remove_section_config}
                    for section in data["sections_config"]
                ]
                assert expected_file["expected_output"]["fund_config"] == data["fund_config"]
                assert expected_file["expected_output"]["round_config"] == data["round_config"]
                assert expected_file["expected_output"]["sections_config"] == data["sections_config"]
            else:
                assert data == expected_file["expected_output"]


def test_generate_config_for_round_invalid_input(seed_dynamic_data):
    # Setup: Prepare invalid input parameters
    round_id = None
    # Execute and Assert: Ensure the function raises an exception for invalid inputs
    with pytest.raises(ValueError):
        generate_config_for_round(round_id)


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
            + '<div class="govuk-!-margin-bottom-8">\n  <h2 class="govuk-heading-m ">\n    Table of contents\n  </h2>\n  <ol class="govuk-list govuk-list--number">\n    <li>\n      <a class="govuk-link" href="#organisation-information">\n        Organisation Information\n      </a>\n    </li>\n  </ol>\n  <hr class="govuk-section-break govuk-section-break--l govuk-section-break--visible" />\n  <h2 class="govuk-heading-l" id="organisation-information">\n    1. Organisation Information\n  </h2>\n  <h3 class="govuk-heading-m">\n    1.1. About your organisation\n  </h3>\n  <h4 class="govuk-heading-s">\n    1.1.1. Organisation Name\n  </h4>\n  <div class="govuk-body all-questions-component">\n    <p class="govuk-body">\n      What is your organisation\'s name?\n    </p>\n    <p class="govuk-body">\n      This must match the registered legal organisation name\n    </p>\n  </div>\n  <div class="govuk-body all-questions-component">\n    <p class="govuk-body">\n      How is your organisation classified?\n    </p>\n    <ul class="govuk-list govuk-list--bullet">\n      <li class="">\n        Charity\n      </li>\n      <li class="">\n        Public Limited Company\n      </li>\n    </ul>\n  </div>\n</div>'  # noqa: E501
            + frontend_html_suffix,
        }
    ]
    for expected_file in expected_files:
        path = expected_file["path"]
        assert path.exists(), f"Expected file {path} does not exist."

    with open(expected_file["path"], "r") as file:
        data = file.read()
        assert data == expected_file["expected_output"]


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
    output = create_export_zip(directory_to_zip=test_data_path, zip_file_name="test_zip")
    assert output
    output_path = Path(output)
    assert output_path.exists()
