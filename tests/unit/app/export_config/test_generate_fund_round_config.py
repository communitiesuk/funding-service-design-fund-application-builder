import ast

import pytest

from app.export_config.generate_fund_round_config import generate_config_for_round


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
    fund_config, round_config = generate_config_for_round(round_id)
    # Simply writes the files to the output directory so no result is given directly
    assert fund_config is not None
    assert round_config is not None
    # Assert: Check if the directory structure and files are created as expected
    expected_files = [
        {
            "path": temp_output_dir / round_short_name / "fund_store" / f"{str.lower(fund_short_name)}.py",
            "expected_output": {
                "sections_config": [
                    {
                        "section_name": {"en": "1. Organisation Information", "cy": ""},
                        "requires_feedback": None,
                    },
                    {
                        "section_name": {"en": "1.1 about-your-org", "cy": ""},
                        "form_name_json": {"en": "about-your-org", "cy": ""},
                    },
                ],
                "fund_config": {
                    "short_name": fund_short_name,
                    "welsh_available": False,
                    "owner_organisation_name": None,
                    "owner_organisation_shortname": None,
                    "owner_organisation_logo_uri": None,
                    "name_json": {"en": "Unit Test Fund 1"},
                    "title_json": {"en": "funding to improve testing"},
                    "description_json": {"en": "A £10m fund to improve testing across the devolved nations."},
                    "funding_type": "COMPETITIVE",
                    "ggis_scheme_reference_number": "G3-SCH-0000092414",
                },
                "round_config": {
                    "short_name": round_short_name,
                    "application_reminder_sent": False,
                    "prospectus": "https://www.google.com",
                    "privacy_notice": "https://www.google.com",
                    "contact_email": "test@test.com",
                    "instructions_json": None,
                    "feedback_link": "https://www.google.com",
                    "project_name_field_id": "12312312312",
                    "application_guidance_json": None,
                    "guidance_url": "https://www.google.com",
                    "all_uploaded_documents_section_available": False,
                    "application_fields_download_available": False,
                    "display_logo_on_pdf_exports": False,
                    "mark_as_complete_enabled": False,
                    "is_expression_of_interest": False,
                    "eoi_decision_schema": {"en": {"valid": True}, "cy": {"valid": False}},
                    "feedback_survey_config": {
                        "has_feedback_survey": False,
                        "has_section_feedback": False,
                        "has_research_survey": False,
                        "is_feedback_survey_optional": False,
                        "is_section_feedback_optional": False,
                        "is_research_survey_optional": False,
                    },
                    "eligibility_config": {"has_eligibility": False},
                    "title_json": {"en": "round the first"},
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
