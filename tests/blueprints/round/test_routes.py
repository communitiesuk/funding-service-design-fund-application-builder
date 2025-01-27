import pytest
from bs4 import BeautifulSoup
from flask import g, url_for

from app.db.models import Round
from app.db.queries.round import get_round_by_id
from tests.helpers import submit_form

round_data_info = {
    "opens": ["01", "10", "2024", "09", "00"],
    "deadline": ["01", "12", "2024", "17", "00"],
    "assessment_start": ["02", "12", "2024", "09", "00"],
    "reminder_date": ["15", "11", "2024", "09", "00"],
    "assessment_deadline": ["15", "12", "2024", "17", "00"],
    "prospectus_link": "https://example.com/prospectus",
    "privacy_notice_link": "https://example.com/privacy",
    "contact_email": "contact@example.com",
    "contact_phone": "1234567890",
    "contact_textphone": "0987654321",
    "support_times": "9am - 5pm",
    "support_days": "Monday to Friday",
    "feedback_link": "https://example.com/feedback",
    "project_name_field_id": 1,
    "guidance_url": "https://example.com/guidance",
}


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_select_fund(flask_test_client, seed_dynamic_data):
    """
    Test the /rounds/select-grant route to ensure a user cannot proceed without selecting a fund
    and is redirected to /rounds/create if a valid fund is selected.
    """
    url = "/rounds/select-grant"

    # Attempt to submit without a fund selected
    response = submit_form(flask_test_client, url, {"fund_id": ""})
    assert response.status_code == 200  # Returns form with errors
    assert b"There is a problem" in response.data  # Validation error message

    # Submit with a valid fund
    test_fund = seed_dynamic_data["funds"][0]
    response = submit_form(flask_test_client, url, {"fund_id": str(test_fund.fund_id)}, follow_redirects=False)
    assert response.status_code == 302

    # Confirm redirect to /rounds/create?fund_id=...
    expected_location = url_for("round_bp.create_round", fund_id=test_fund.fund_id)
    assert response.location == expected_location


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_round_with_existing_short_name(flask_test_client, seed_dynamic_data):
    """
    Tests that a round can be successfully created using the /rounds/create route
    Verifies that the created round has the correct attributes
    """
    test_fund = seed_dynamic_data["funds"][0]
    new_round_data = {
        "fund_id": test_fund.fund_id,
        "title_en": "New Round",
        "short_name": "NR123",
        "save_and_return_home": True,
        **round_data_info,
    }

    error_html = '<a href="#short_name">Given short name already exists in the fund funding to improve testing.</a>'
    url = f"/rounds/create?fund_id={test_fund.fund_id}"

    # Test works fine with first round
    response = submit_form(flask_test_client, url, new_round_data)
    assert response.status_code == 200
    assert error_html not in response.data.decode("utf-8"), "Error HTML found in response"

    # Test works fine with second round but with different short name
    new_round_data["short_name"] = "NR1234"
    response = submit_form(flask_test_client, url, new_round_data)
    assert response.status_code == 200
    assert error_html not in response.data.decode("utf-8"), "Error HTML found in response"

    # Test doesn't work with third round with same short name as first
    new_round_data["short_name"] = "NR123"
    response = submit_form(flask_test_client, url, new_round_data)
    assert response.status_code == 200
    assert error_html in response.data.decode("utf-8"), "Error HTML not found in response"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_update_existing_round(flask_test_client, seed_dynamic_data):
    """
    Tests that a round can be successfully updated using the /rounds/<round_id> route
    Verifies that the updated round has the correct attributes
    """
    update_round_data = {
        "fund_id": seed_dynamic_data["funds"][0].fund_id,
        "title_en": "Updated Round",
        "short_name": "UR123",
        "save_and_continue": True,
        **round_data_info,
    }
    update_round_data.update({"has_feedback_survey": "true"})

    test_round = seed_dynamic_data["rounds"][0]
    response = submit_form(flask_test_client, f"/rounds/{test_round.round_id}/edit", update_round_data)
    assert response.status_code == 200

    updated_round = get_round_by_id(test_round.round_id)
    assert updated_round.title_json["en"] == "Updated Round"
    assert updated_round.short_name == "UR123"
    assert updated_round.feedback_survey_config == {
        "has_feedback_survey": True,
        "has_section_feedback": False,
        "has_research_survey": False,
        "is_feedback_survey_optional": False,
        "is_section_feedback_optional": False,
        "is_research_survey_optional": False,
    }

    assert response.request.path == f"/rounds/{test_round.round_id}"
    soup = BeautifulSoup(response.data, "html.parser")
    notification = soup.find("h3", {"class": "govuk-notification-banner__heading"})
    assert notification.text.strip() == "Application updated"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_round_with_return_home(flask_test_client, seed_dynamic_data):
    """Tests that 'Save and return home' action correctly redirects to dashboard after round creation"""
    test_fund = seed_dynamic_data["funds"][0]
    new_round_data = {
        "title_en": "New Round",
        "short_name": "NR456",
        "fund_id": test_fund.fund_id,
        "save_and_return_home": True,
        **round_data_info,
    }

    response = submit_form(
        flask_test_client, f"/rounds/create?fund_id={test_fund.fund_id}&action=return_home", new_round_data
    )
    new_round = Round.query.filter_by(short_name="NR456").first()
    assert new_round is not None
    assert new_round.title_json["en"] == "New Round"
    assert new_round.short_name == "NR456"

    assert response.request.path == "/dashboard"
    soup = BeautifulSoup(response.data, "html.parser")
    notification = soup.find("h3", {"class": "govuk-notification-banner__heading"})
    assert notification.text.strip() == "New application created"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_round_from_application_list(flask_test_client, seed_dynamic_data):
    """Tests that 'Save and return to applications list'
    action correctly redirects to application list after round creation"""
    test_fund = seed_dynamic_data["funds"][0]
    new_round_data = {
        "title_en": "New Round",
        "short_name": "NR456",
        "fund_id": test_fund.fund_id,
        "save_and_continue": True,
        **round_data_info,
    }

    response = submit_form(
        flask_test_client, f"/rounds/create?fund_id={test_fund.fund_id}&action=applications_table", new_round_data
    )
    assert response.request.path == "/rounds/"
    soup = BeautifulSoup(response.data, "html.parser")
    notification = soup.find("h3", {"class": "govuk-notification-banner__heading"})
    assert notification.text.strip() == "New application created"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_round_from_application_list_and_return_to_home(flask_test_client, seed_dynamic_data):
    """Tests that 'Save and return home' action correctly redirects to dashboard after round creation"""
    test_fund = seed_dynamic_data["funds"][0]
    new_round_data = {
        "title_en": "New Round",
        "short_name": "NR456",
        "fund_id": test_fund.fund_id,
        "save_and_return_home": True,
        **round_data_info,
    }

    response = submit_form(
        flask_test_client, f"/rounds/create?fund_id={test_fund.fund_id}&action=applications_table", new_round_data
    )
    assert response.request.path == "/dashboard"
    soup = BeautifulSoup(response.data, "html.parser")
    notification = soup.find("h3", {"class": "govuk-notification-banner__heading"})
    assert notification.text.strip() == "New application created"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_round_from_dashboard_and_continue_build(flask_test_client, seed_dynamic_data):
    """Tests that 'Save and continue build application'
    action correctly redirects to build application after round creation"""
    test_fund = seed_dynamic_data["funds"][0]
    new_round_data = {
        "title_en": "New Round",
        "short_name": "NR456",
        "fund_id": test_fund.fund_id,
        "save_and_continue": True,
        **round_data_info,
    }

    response = submit_form(
        flask_test_client, f"/rounds/create?fund_id={test_fund.fund_id}&action=return_home", new_round_data
    )
    new_round_id = response.request.path.split("/")[-2]
    assert response.request.path == f"/rounds/{new_round_id}/sections"
    soup = BeautifulSoup(response.data, "html.parser")
    notification = soup.find("h3", {"class": "govuk-notification-banner__heading"})
    assert notification.text.strip() == "New application created"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_all_applications_page(flask_test_client, seed_dynamic_data):
    response = flask_test_client.get(
        "/rounds", follow_redirects=True, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200
    html = response.data.decode("utf-8")

    # Title component availability check
    assert '<h1 class="govuk-heading-l">' in html, "Heading title component is missing"
    assert "Applications" in html, "Heading title is missing"

    # Description component availability check
    assert '<p class="govuk-body">' in html, "Description component is missing"
    assert "View existing applications or create a new one." in html, "Description is missing"

    # Button component availability check
    assert "Create new application" in html, "Button text is missing"

    # Table component availability check and data testing
    assert '<thead class="govuk-table__head">' in html, "Table is missing"
    assert '<th scope="col" class="govuk-table__header">Application name</th>' in html, (
        "Application Name header is missing"
    )
    assert '<th scope="col" class="govuk-table__header">Grant</th>' in html, "Grant name header missing"
    assert '<th scope="col" class="govuk-table__header">Round</th>' in html, "Grant name header missing"

    assert "Apply for funding to improve testing" in html, "Application name is missing"
    assert "funding to improve testing" in html, "Grant name and table component is missing"
    assert "round the first" in html, "Round name and table component is missing"
    assert "Build application" in html, "Build application is not available and table component is missing"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_view_round_details(flask_test_client, seed_dynamic_data):
    """
    Test to check round detail route is working as expected.
    and verify the round details template is rendered as expected.
    """

    test_round = seed_dynamic_data["rounds"][0]
    test_fund = seed_dynamic_data["funds"][0]
    response = flask_test_client.get(f"/rounds/{test_round.round_id}", follow_redirects=True)
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")
    heading = soup.find("h2", {"class": "govuk-heading-l"})
    assert heading.text.strip() == "Apply for " + test_fund.title_json["en"]

    fundname = soup.find("p", {"class": "govuk-body"})
    assert fundname.text.strip() == "Grant: " + test_fund.name_json["en"]

    backlink = soup.find("a", {"class": "govuk-back-link"})
    assert backlink.text == "Back"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_clone_round(flask_test_client, seed_dynamic_data):
    """
    Test to check round detail route is working as expected.
    and verify the round details template is rendered as expected.
    """

    test_round = seed_dynamic_data["rounds"][0]
    test_fund = seed_dynamic_data["funds"][0]
    response = flask_test_client.get(f"/rounds/{test_round.round_id}", follow_redirects=True)
    assert response.status_code == 200
    with flask_test_client.session_transaction():
        url = url_for("round_bp.clone_round", round_id=test_round.round_id)
        response = flask_test_client.post(
            url,
            data={"fund_id": test_fund.fund_id, "csrf_token": g.csrf_token},
            follow_redirects=True,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        soup = BeautifulSoup(response.data, "html.parser")
        notification = soup.find("div", {"class": "govuk-notification-banner__content"})
        assert notification.text.strip() == "Application copied"
        copied_round_id = response.request.path.split("/")[-1]
        expected_application_name = f"Copy of {test_round.title_json['en']}"

        assert f"Copy of {test_round.title_json['en']}" in soup.text
        updated_round = get_round_by_id(copied_round_id)
        assert updated_round.title_json["en"] == expected_application_name

        response = flask_test_client.post(
            url,
            data={"csrf_token": g.csrf_token},
            follow_redirects=True,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        soup = BeautifulSoup(response.data, "html.parser")
        notification = soup.find("div", {"class": "govuk-notification-banner__content"})
        assert notification.text.strip() == "Error copying application"
