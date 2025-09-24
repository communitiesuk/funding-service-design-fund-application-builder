import json
from unittest.mock import MagicMock, patch

import pytest

from app.export_config.generate_fund_round_form_jsons import generate_form_jsons_for_round
from app.shared.form_store_api import PublishedFormResponse
from tests.seed_test_data import ABOUT_YOUR_ORG_FORM_JSON


@patch("app.export_config.generate_fund_round_form_jsons.FormStoreAPIService")
def test_generate_form_jsons_for_round_valid_input(mock_api_service_class, seed_dynamic_data, temp_output_dir):
    # Setup mock
    mock_api_service = MagicMock()

    # Create a PublishedFormResponse object with the test data
    mock_published_form = PublishedFormResponse(
        id="test-form-id",
        url_path="about-your-org",
        display_name="About your organisation",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        published_at="2024-01-01T00:00:00Z",
        is_published=True,
        published_json=ABOUT_YOUR_ORG_FORM_JSON,
        hash="test-hash-123",
    )

    mock_api_service.get_published_form.return_value = mock_published_form
    mock_api_service_class.return_value = mock_api_service

    # Setup: Prepare valid input parameters
    round_id = seed_dynamic_data["rounds"][0].round_id
    round_short_name = seed_dynamic_data["rounds"][0].short_name
    form_publish_name = seed_dynamic_data["forms"][0].runner_publish_name

    # Execute: Call the function with valid inputs
    generate_form_jsons_for_round(round_id)

    # Assert: Check if the directory structure and files are created as expected
    expected_file = {
        "path": temp_output_dir / round_short_name / "form_runner" / f"{form_publish_name}.json",
        "expected_output": {
            "startPage": "/organisation-name",
            "pages": [
                {
                    "path": "/organisation-name",
                    "title": "Organisation Name",
                    "components": [
                        {
                            "name": "organisation_name",
                            "options": {"hideTitle": False, "classes": ""},
                            "type": "TextField",
                            "title": "What is your organisation's name?",
                            "hint": "This must match the registered legal organisation name",
                            "schema": {},
                        }
                    ],
                    "next": [{"path": "/organisation-alternative-names"}],
                },
                {
                    "path": "/organisation-alternative-names",
                    "title": "Alternative names of your organisation",
                    "components": [
                        {
                            "name": "alt_name_1",
                            "options": {},
                            "type": "TextField",
                            "title": "Alternative name 1",
                            "schema": {},
                        }
                    ],
                    "next": [{"path": "/organisation-address"}],
                },
                {
                    "path": "/organisation-address",
                    "title": "Organisation Address",
                    "components": [
                        {
                            "name": "organisation_address",
                            "options": {},
                            "type": "UkAddressField",
                            "title": "What is your organisation's address?",
                            "schema": {},
                        }
                    ],
                    "next": [{"path": "/organisation-classification"}],
                },
                {
                    "path": "/organisation-classification",
                    "title": "Organisation Classification",
                    "components": [
                        {
                            "name": "organisation_classification",
                            "options": {"hideTitle": False, "classes": ""},
                            "type": "RadiosField",
                            "title": "How is your organisation classified?",
                            "list": "classifications_list",
                            "schema": {},
                        }
                    ],
                    "next": [{"path": "/summary"}],
                },
                {
                    "path": "/summary",
                    "title": "Check your answers",
                    "components": [],
                    "next": [],
                    "controller": "./pages/summary.js",
                },
            ],
            "lists": [
                {
                    "name": "classifications_list",
                    "type": "string",
                    "items": [
                        {"text": "Charity", "value": "charity"},
                        {"text": "Public Limited Company", "value": "plc"},
                    ],
                }
            ],
            "conditions": [],
            "sections": [],
            "outputs": [],
            "skipSummary": False,
            "name": "About your organisation",
        },
    }
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
