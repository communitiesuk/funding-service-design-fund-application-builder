import secrets
import string
from pathlib import Path
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from flask import g, url_for

from app.blueprints.application.routes import create_export_zip
from app.shared.form_store_api import FormResponse, PublishedFormResponse
from tests.helpers import find_button_with_text, submit_form


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_select_application_invalid_access(flask_test_client):
    """Test that proper errors are raised for invalid access attempts"""
    # Test access without fund ID
    with pytest.raises(ValueError, match="Fund ID is required to manage an application"):
        flask_test_client.get("/rounds/sections/select-application", follow_redirects=True)

    # Test access with invalid fund ID
    invalid_fund_id = "123e4567-e89b-12d3-a456-426614174000"
    with pytest.raises(ValueError, match=f"Fund with id {invalid_fund_id} not found"):
        flask_test_client.get(f"/rounds/sections/select-application?fund_id={invalid_fund_id}", follow_redirects=True)


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
@patch("app.blueprints.application.routes.FormStoreAPIService")
def test_create_section(mock_form_store_service, flask_test_client, seed_dynamic_data):
    # Mock the API service
    mock_published_form = type(
        "MockForm", (), {"url_path": "about-your-org", "display_name": "About your organisation"}
    )
    mock_form_store_service.return_value.get_published_forms.return_value = [mock_published_form]

    test_round = seed_dynamic_data["rounds"][0]
    url = f"/rounds/{test_round.round_id}/sections/create"
    data = {"name_in_apply_en": "section 1", "save_section": True}
    response = submit_form(flask_test_client, url, data, follow_redirects=True)

    soup = BeautifulSoup(response.data, "html.parser")
    section = soup.find("h3", class_="govuk-heading-m", string="2. section 1")
    assert section


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
@patch("app.blueprints.application.routes.FormStoreAPIService")
def test_update_section_name(mock_form_store_service, flask_test_client, seed_dynamic_data):
    # Mock the API service
    mock_published_form = type(
        "MockForm", (), {"url_path": "about-your-org", "display_name": "About your organisation"}
    )
    mock_form_store_service.return_value.get_published_forms.return_value = [mock_published_form]

    test_round = seed_dynamic_data["rounds"][0]
    url = f"/rounds/{test_round.round_id}/sections/create"
    data = {"name_in_apply_en": "section 1", "save_section": True}
    response = submit_form(flask_test_client, url, data, follow_redirects=True)
    soup = BeautifulSoup(response.data, "html.parser")
    edit_section_link = find_button_with_text(soup, "Edit", "govuk-button--secondary").get("href")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
@patch("app.blueprints.application.routes.FormStoreAPIService")
def test_delete_section(mock_form_store_service, flask_test_client, seed_dynamic_data):
    # Mock the API service
    mock_published_form = type(
        "MockForm", (), {"url_path": "about-your-org", "display_name": "About your organisation"}
    )
    mock_form_store_service.return_value.get_published_forms.return_value = [mock_published_form]

    test_round = seed_dynamic_data["rounds"][0]
    url = f"/rounds/{test_round.round_id}/sections/create"
    data = {"name_in_apply_en": "section 1", "save_section": True}
    response = submit_form(flask_test_client, url, data, follow_redirects=True)
    soup = BeautifulSoup(response.data, "html.parser")
    edit_section_link = find_button_with_text(soup, "Edit", "govuk-button--secondary").get("href")
    section_id = edit_section_link.split("/")[-1]

    delete_section_link = f"/rounds/{test_round.round_id}/sections/{section_id}/delete"
    delete_confirmation_response = flask_test_client.get(delete_section_link)
    soup = BeautifulSoup(delete_confirmation_response.data, "html.parser")
    confirmation_heading = soup.find("h1", class_="govuk-panel__title")
    assert delete_confirmation_response.status_code == 200
    assert confirmation_heading.text == "Are you sure you want to delete this section?"

    response = submit_form(
        flask_test_client,
        delete_section_link,
        data={
            "csrf_token": g.csrf_token,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
@patch("app.blueprints.application.routes.FormStoreAPIService")
def test_update_section_empty_template_section_name(mock_form_store_service, flask_test_client, seed_dynamic_data):
    # Mock the API service
    mock_published_form = type(
        "MockForm", (), {"url_path": "about-your-org", "display_name": "About your organisation"}
    )
    mock_form_store_service.return_value.get_published_forms.return_value = [mock_published_form]

    test_round = seed_dynamic_data["rounds"][0]
    url = f"/rounds/{test_round.round_id}/sections/create"
    data = {"name_in_apply_en": "section 1", "save_section": True}
    response = submit_form(flask_test_client, url, data, follow_redirects=True)
    soup = BeautifulSoup(response.data, "html.parser")
    edit_section_link = find_button_with_text(soup, "Edit", "govuk-button--secondary").get("href")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_add_form_to_section(flask_test_client, seed_dynamic_data, mocker):
    test_form = seed_dynamic_data["forms"][0]

    form_data = {
        "id": "test-form-id",
        "url_path": test_form.url_path,
        "display_name": "About your organisation",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "published_at": "2024-01-01T00:00:00Z",
        "is_published": True,
    }

    mock_api_service = mocker.Mock()
    mock_api_service.get_published_forms.return_value = [FormResponse(**form_data)]
    mock_api_service.get_published_form.return_value = PublishedFormResponse(
        **form_data, published_json={"pages": []}, hash="test-hash"
    )
    mock_api_service.get_display_name_from_url_path.return_value = "About your organisation"

    mocker.patch("app.blueprints.application.routes.FormStoreAPIService", return_value=mock_api_service)
    mocker.patch("app.db.queries.application.FormStoreAPIService", return_value=mock_api_service)

    test_round = seed_dynamic_data["rounds"][0]
    url = f"/rounds/{test_round.round_id}/sections/create"
    data = {"name_in_apply_en": "section 1", "save_section": True}
    response = submit_form(flask_test_client, url, data, follow_redirects=True)
    soup = BeautifulSoup(response.data, "html.parser")
    edit_section_link = find_button_with_text(soup, "Edit", "govuk-button--secondary").get("href")
    data = {
        "name_in_apply_en": "",
        "add_form": True,
        "section_id": edit_section_link.split("/")[-1],
        "template_id": test_form.url_path,
    }

    response = submit_form(flask_test_client, edit_section_link, data, follow_redirects=False)
    soup = BeautifulSoup(response.data, "html.parser")
    spans_with_h3 = soup.find_all("span", class_="app-task-list__task-name")
    found = False

    for span in spans_with_h3:
        h3_tag = span.find("h3", class_="govuk-body")
        if h3_tag and "1. About your organisation" in h3_tag.get_text():
            found = True
            break

    assert found, "Template Form not found"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
@patch("app.blueprints.application.routes.FormStoreAPIService")
def test_mark_application_complete(mock_form_store_service, flask_test_client, seed_dynamic_data):
    """Test marking an application as complete"""
    # Mock the API service
    mock_published_form = type(
        "MockForm", (), {"url_path": "about-your-org", "display_name": "About your organisation"}
    )
    mock_form_store_service.return_value.get_published_forms.return_value = [mock_published_form]

    test_round = seed_dynamic_data["rounds"][0]

    # Ensure the round starts with "In progress" status
    assert test_round.status == "In progress"

    # Call the endpoint to mark application as complete (don't follow redirects)
    url = f"/rounds/{test_round.round_id}/mark-complete"
    response = flask_test_client.get(url, follow_redirects=False)
    assert response.status_code == 302  # Should be a redirect

    # Now manually go to the build_application page to check the status
    app_url = f"/rounds/{test_round.round_id}/sections"
    response = flask_test_client.get(app_url)
    assert response.status_code == 200

    # Check the page content reflects the completed status
    soup = BeautifulSoup(response.data, "html.parser")

    # Title should be "View application"
    assert soup.find("h1", class_="govuk-heading-l").text.strip() == "View application"

    # Status tag should be green
    status_tag = soup.find("span", class_="govuk-tag")
    assert "govuk-tag--green" in status_tag["class"]
    assert status_tag.text.strip() == "Complete"

    # "Edit application" button should be visible
    edit_button = soup.find("a", string=lambda text: "Edit application" in text if text else False)
    assert edit_button is not None

    # "Mark application complete" button should NOT be visible
    complete_button = soup.find("a", string=lambda text: "Mark application complete" in text if text else False)
    assert complete_button is None

    # "Add section" button should NOT be visible
    add_section_button = soup.find("a", string=lambda text: "Add section" in text if text else False)
    assert add_section_button is None

    # "Edit", "Up", "Down" buttons for sections should NOT be visible
    edit_buttons = soup.find_all("a", string="Edit")
    assert len(edit_buttons) == 0
    up_links = soup.find_all("a", string="Up")
    assert len(up_links) == 0
    down_links = soup.find_all("a", string="Down")
    assert len(down_links) == 0


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_application_complete_page(flask_test_client, seed_dynamic_data):
    """Test the application complete confirmation page"""
    test_round = seed_dynamic_data["rounds"][0]

    # Call the endpoint to mark application as complete and follow redirects
    url = f"/rounds/{test_round.round_id}/mark-complete"
    response = flask_test_client.get(url, follow_redirects=True)
    assert response.status_code == 200

    # Check the confirmation page content
    soup = BeautifulSoup(response.data, "html.parser")

    # Check for the confirmation panel
    panel = soup.find("div", class_="govuk-panel--confirmation")
    assert panel is not None

    # Check panel title
    panel_title = panel.find("h1", class_="govuk-panel__title")
    assert panel_title is not None
    assert panel_title.text.strip() == "Application marked as complete"

    # Check for the status change text
    status_text = soup.find(
        "p",
        class_="govuk-body",
        string=lambda text: "You can still edit your application at any time" in text if text else False,
    )
    assert status_text is not None

    # Check for the "What happens next" heading
    next_heading = soup.find("h3", class_="govuk-heading-m", string="What you need to do next")
    assert next_heading is not None

    # Check for the back to application link
    back_link = soup.find("a", string="Back to application")
    assert back_link is not None

    # Check for the go to home link
    home_link = soup.find("a", string="Go to home page")
    assert home_link is not None


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
@patch("app.blueprints.application.routes.FormStoreAPIService")
def test_mark_application_in_progress(mock_form_store_service, flask_test_client, seed_dynamic_data):
    """Test marking a complete application as in progress"""
    # Mock the API service
    mock_published_form = type(
        "MockForm", (), {"url_path": "about-your-org", "display_name": "About your organisation"}
    )
    mock_form_store_service.return_value.get_published_forms.return_value = [mock_published_form]

    test_round = seed_dynamic_data["rounds"][0]

    # First mark the application as complete
    flask_test_client.get(f"/rounds/{test_round.round_id}/mark-complete")

    # Then mark it back as in progress
    url = f"/rounds/{test_round.round_id}/mark-in-progress"
    response = flask_test_client.get(url, follow_redirects=True)
    assert response.status_code == 200

    # Check the page content reflects the in-progress status
    soup = BeautifulSoup(response.data, "html.parser")

    # Title should be "Build application"
    assert soup.find("h1", class_="govuk-heading-l").text.strip() == "Build application"

    # Status tag should be blue
    status_tag = soup.find("span", class_="govuk-tag")
    assert "govuk-tag--blue" in status_tag["class"]
    assert status_tag.text.strip() == "In progress"

    # "Edit application" button should NOT be visible
    edit_button = soup.find("a", string=lambda text: "Edit application" in text if text else False)
    assert edit_button is None

    # "Mark application complete" button should be visible
    complete_button = soup.find("a", string=lambda text: "Mark application complete" in text if text else False)
    assert complete_button is not None

    # "Add section" button should be visible
    add_section_button = soup.find("a", string=lambda text: "Add section" in text if text else False)
    assert add_section_button is not None

    # If there are sections, "Edit", "Up", "Down" buttons should be visible
    # We need to create a section first to test this
    if len(seed_dynamic_data["rounds"][0].sections) > 0:
        edit_buttons = soup.find_all("a", string="Edit")
        assert len(edit_buttons) > 0


def test_create_export_zip(temp_output_dir):
    test_data_path = Path("tests") / "test_data"
    random_post_fix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    output = create_export_zip(
        directory_to_zip=test_data_path, zip_file_name="test_zip", random_post_fix=random_post_fix
    )
    assert output
    output_path = Path(output)
    assert output_path.exists()
