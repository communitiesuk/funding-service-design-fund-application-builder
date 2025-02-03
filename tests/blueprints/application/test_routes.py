import pytest
from bs4 import BeautifulSoup
from flask import url_for

from tests.helpers import submit_form


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_select_fund(flask_test_client, seed_dynamic_data):
    """
    Test the /rounds/sections/select-grant route to ensure:
      1) A user cannot proceed without selecting a fund,
      2) A valid fund selection redirects to the select_application page.
    """
    url = "/rounds/sections/select-grant"

    # Attempt to submit without a fund selected
    response = submit_form(flask_test_client, url, {"fund_id": ""})
    assert response.status_code == 200  # Returns form with errors
    assert b"There is a problem" in response.data  # Validation error message

    # Submit with a valid fund
    test_fund = seed_dynamic_data["funds"][0]
    response = submit_form(flask_test_client, url, {"fund_id": str(test_fund.fund_id)}, follow_redirects=False)
    assert response.status_code == 302

    # Confirm redirect to /rounds/sections/select-application?fund_id=...
    expected_location = url_for("application_bp.select_application", fund_id=test_fund.fund_id)
    assert response.location == expected_location


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_select_application_invalid_access(flask_test_client):
    """Test that proper errors are raised for invalid access attempts"""
    # Test access without fund ID
    with pytest.raises(ValueError, match="Fund ID is required to manage an application"):
        flask_test_client.get("/rounds/sections/select-application", follow_redirects=True)

    # Test access with invalid fund ID
    invalid_fund_id = "123e4567-e89b-12d3-a456-426614174000"
    with pytest.raises(ValueError, match=f"Fund with id {invalid_fund_id} not found"):
        flask_test_client.get(f"/rounds/sections/select-application?fund_id={invalid_fund_id}", follow_redirects=True)


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_select_application_form_submission(flask_test_client, seed_dynamic_data):
    """Test the actual form submission functionality"""
    test_fund = seed_dynamic_data["funds"][0]
    url = f"/rounds/sections/select-application?fund_id={test_fund.fund_id}"

    # Attempt to submit without a round selected
    response = submit_form(flask_test_client, url, {"round_id": ""})
    assert response.status_code == 200  # Returns form with errors
    assert b"There is a problem" in response.data  # Validation error message

    # Submit with a valid round
    test_round = seed_dynamic_data["rounds"][0]
    response = submit_form(flask_test_client, url, {"round_id": str(test_round.round_id)}, follow_redirects=False)
    assert response.status_code == 302

    # Confirm redirect to application_bp.build_application
    expected_location = url_for("application_bp.build_application", round_id=test_round.round_id)
    assert response.location == expected_location


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_section(flask_test_client, seed_dynamic_data):
    test_round = seed_dynamic_data["rounds"][0]
    url = f"/rounds/{test_round.round_id}/sections/create"
    data = {"name_in_apply_en": "section 1", "save_section": True}
    response = submit_form(flask_test_client, url, data, follow_redirects=True)

    soup = BeautifulSoup(response.data, "html.parser")
    section = soup.find("h3", class_="govuk-heading-m", string="2. section 1")
    assert section


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_update_section_name(flask_test_client, seed_dynamic_data):
    test_round = seed_dynamic_data["rounds"][0]
    url = f"/rounds/{test_round.round_id}/sections/create"
    data = {"name_in_apply_en": "section 1", "save_section": True}
    response = submit_form(flask_test_client, url, data, follow_redirects=True)
    soup = BeautifulSoup(response.data, "html.parser")
    edit_section_link = soup.find("a", class_="govuk-link--no-visited-state", string="Edit").get("href")
    data = {
        "name_in_apply_en": "section updated",
        "save_section": True,
        "section_id": edit_section_link.split("/")[-1],
        "template_id": "",
    }

    response = submit_form(flask_test_client, edit_section_link, data, follow_redirects=True)
    soup = BeautifulSoup(response.data, "html.parser")
    section = soup.find("h3", class_="govuk-heading-m", string="1. section updated")
    assert section


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_update_section_empty_template_section_name(flask_test_client, seed_dynamic_data):
    test_round = seed_dynamic_data["rounds"][0]
    url = f"/rounds/{test_round.round_id}/sections/create"
    data = {"name_in_apply_en": "section 1", "save_section": True}
    response = submit_form(flask_test_client, url, data, follow_redirects=True)
    soup = BeautifulSoup(response.data, "html.parser")
    edit_section_link = soup.find("a", class_="govuk-link--no-visited-state", string="Edit").get("href")
    data = {"name_in_apply_en": "", "add_form": True, "section_id": edit_section_link.split("/")[-1], "template_id": ""}

    response = submit_form(flask_test_client, edit_section_link, data, follow_redirects=False)
    soup = BeautifulSoup(response.data, "html.parser")
    error_link = soup.find("a", href="#template_id")
    assert error_link
    assert error_link.get_text() == "Select a template"

    data = {
        "name_in_apply_en": "",
        "save_section": True,
        "section_id": edit_section_link.split("/")[-1],
        "template_id": "",
    }

    response = submit_form(flask_test_client, edit_section_link, data, follow_redirects=False)
    soup = BeautifulSoup(response.data, "html.parser")
    error_link = soup.find("a", href="#name_in_apply_en")
    assert error_link
    assert error_link.get_text() == "Enter section name"
