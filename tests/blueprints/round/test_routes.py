import pytest
from flask import url_for

from app.db.models import Round
from app.db.queries.round import get_round_by_id
from tests.helpers import submit_form


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_select_fund(flask_test_client, seed_dynamic_data):
    """
    Test the /applications/select-grant route to ensure a user cannot proceed without selecting a fund
    and is redirected to /applications/create if a valid fund is selected.
    """
    url = "/applications/select-grant"

    # Attempt to submit without a fund selected
    response = submit_form(flask_test_client, url, {"fund_id": ""})
    assert response.status_code == 200  # Returns form with errors
    assert b"There is a problem" in response.data  # Validation error message

    # Submit with a valid fund
    test_fund = seed_dynamic_data["funds"][0]
    response = submit_form(flask_test_client, url, {"fund_id": str(test_fund.fund_id)}, follow_redirects=False)
    assert response.status_code == 302

    # Confirm redirect to /applications/create?fund_id=...
    expected_location = url_for("round_bp.create_round", fund_id=test_fund.fund_id)
    assert response.location == expected_location


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_round_with_existing_short_name(flask_test_client, seed_dynamic_data):
    """
    Tests that a round can be successfully created using the /applications/create route
    Verifies that the created round has the correct attributes
    """
    test_fund = seed_dynamic_data["funds"][0]
    new_round_data = {
        "fund_id": test_fund.fund_id,
        "title_en": "New Round",
        "short_name": "NR123",
        "opens-day": "01",
        "opens-month": "10",
        "opens-year": "2024",
        "opens-hour": "09",
        "opens-minute": "00",
        "deadline-day": "01",
        "deadline-month": "12",
        "deadline-year": "2024",
        "deadline-hour": "17",
        "deadline-minute": "00",
        "assessment_start-day": "02",
        "assessment_start-month": "12",
        "assessment_start-year": "2024",
        "assessment_start-hour": "09",
        "assessment_start-minute": "00",
        "reminder_date-day": "15",
        "reminder_date-month": "11",
        "reminder_date-year": "2024",
        "reminder_date-hour": "09",
        "reminder_date-minute": "00",
        "assessment_deadline-day": "15",
        "assessment_deadline-month": "12",
        "assessment_deadline-year": "2024",
        "assessment_deadline-hour": "17",
        "assessment_deadline-minute": "00",
        "prospectus_link": "http://example.com/prospectus",
        "privacy_notice_link": "http://example.com/privacy",
        "contact_email": "contact@example.com",
        "contact_phone": "1234567890",
        "contact_textphone": "0987654321",
        "support_times": "9am - 5pm",
        "support_days": "Monday to Friday",
        "feedback_link": "http://example.com/feedback",
        "project_name_field_id": 1,
        "guidance_url": "http://example.com/guidance",
    }

    error_html = (
        '<a href="#short_name">Short name: Given short name already exists in the fund funding to improve testing.</a>'
    )
    url = f"/applications/create?fund_id={test_fund.fund_id}"

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
def test_create_new_round(flask_test_client, seed_dynamic_data):
    """
    Tests that a round can be successfully created using the /applications/create route
    Verifies that the created round has the correct attributes
    """
    test_fund = seed_dynamic_data["funds"][0]
    new_round_data = {
        "fund_id": test_fund.fund_id,
        "title_en": "New Round",
        "short_name": "NR123",
        "opens-day": "01",
        "opens-month": "10",
        "opens-year": "2024",
        "opens-hour": "09",
        "opens-minute": "00",
        "deadline-day": "01",
        "deadline-month": "12",
        "deadline-year": "2024",
        "deadline-hour": "17",
        "deadline-minute": "00",
        "assessment_start-day": "02",
        "assessment_start-month": "12",
        "assessment_start-year": "2024",
        "assessment_start-hour": "09",
        "assessment_start-minute": "00",
        "reminder_date-day": "15",
        "reminder_date-month": "11",
        "reminder_date-year": "2024",
        "reminder_date-hour": "09",
        "reminder_date-minute": "00",
        "assessment_deadline-day": "15",
        "assessment_deadline-month": "12",
        "assessment_deadline-year": "2024",
        "assessment_deadline-hour": "17",
        "assessment_deadline-minute": "00",
        "prospectus_link": "http://example.com/prospectus",
        "privacy_notice_link": "http://example.com/privacy",
        "contact_email": "contact@example.com",
        "contact_phone": "1234567890",
        "contact_textphone": "0987654321",
        "support_times": "9am - 5pm",
        "support_days": "Monday to Friday",
        "feedback_link": "http://example.com/feedback",
        "project_name_field_id": 1,
        "guidance_url": "http://example.com/guidance",
    }

    response = submit_form(flask_test_client, f"/applications/create?fund_id={test_fund.fund_id}", new_round_data)
    assert response.status_code == 200

    new_round = Round.query.filter_by(short_name="NR123").first()
    assert new_round is not None
    assert new_round.title_json["en"] == "New Round"
    assert new_round.short_name == "NR123"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_update_existing_round(flask_test_client, seed_dynamic_data):
    """
    Tests that a round can be successfully updated using the /applications/<round_id> route
    Verifies that the updated round has the correct attributes
    """
    update_round_data = {
        "fund_id": seed_dynamic_data["funds"][0].fund_id,
        "title_en": "Updated Round",
        "short_name": "UR123",
        "opens-day": "01",
        "opens-month": "10",
        "opens-year": "2024",
        "opens-hour": "09",
        "opens-minute": "00",
        "deadline-day": "01",
        "deadline-month": "12",
        "deadline-year": "2024",
        "deadline-hour": "17",
        "deadline-minute": "00",
        "assessment_start-day": "02",
        "assessment_start-month": "12",
        "assessment_start-year": "2024",
        "assessment_start-hour": "09",
        "assessment_start-minute": "00",
        "reminder_date-day": "15",
        "reminder_date-month": "11",
        "reminder_date-year": "2024",
        "reminder_date-hour": "09",
        "reminder_date-minute": "00",
        "assessment_deadline-day": "15",
        "assessment_deadline-month": "12",
        "assessment_deadline-year": "2024",
        "assessment_deadline-hour": "17",
        "assessment_deadline-minute": "00",
        "prospectus_link": "http://example.com/updated_prospectus",
        "privacy_notice_link": "http://example.com/updated_privacy",
        "contact_email": "updated_contact@example.com",
        "contact_phone": "1234567890",
        "contact_textphone": "0987654321",
        "support_times": "9am - 5pm",
        "support_days": "Monday to Friday",
        "feedback_link": "http://example.com/feedback",
        "project_name_field_id": 1,
        "guidance_url": "http://example.com/guidance",
        "has_feedback_survey": "true",
    }

    test_round = seed_dynamic_data["rounds"][0]
    response = submit_form(flask_test_client, f"/applications/{test_round.round_id}", update_round_data)
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_round_with_return_home(flask_test_client, seed_dynamic_data):
    """Tests that 'Save and return home' action correctly redirects to dashboard after round creation"""
    test_fund = seed_dynamic_data["funds"][0]
    new_round_data = {
        "fund_id": test_fund.fund_id,
        "title_en": "New Round",
        "short_name": "NR456",
        "opens-day": "01",
        "opens-month": "10",
        "opens-year": "2024",
        "opens-hour": "09",
        "opens-minute": "00",
        "deadline-day": "01",
        "deadline-month": "12",
        "deadline-year": "2024",
        "deadline-hour": "17",
        "deadline-minute": "00",
        "assessment_start-day": "02",
        "assessment_start-month": "12",
        "assessment_start-year": "2024",
        "assessment_start-hour": "09",
        "assessment_start-minute": "00",
        "reminder_date-day": "15",
        "reminder_date-month": "11",
        "reminder_date-year": "2024",
        "reminder_date-hour": "09",
        "reminder_date-minute": "00",
        "assessment_deadline-day": "15",
        "assessment_deadline-month": "12",
        "assessment_deadline-year": "2024",
        "assessment_deadline-hour": "17",
        "assessment_deadline-minute": "00",
        "prospectus_link": "http://example.com/prospectus",
        "privacy_notice_link": "http://example.com/privacy",
        "contact_email": "contact@example.com",
        "contact_phone": "1234567890",
        "contact_textphone": "0987654321",
        "support_times": "9am - 5pm",
        "support_days": "Monday to Friday",
        "feedback_link": "http://example.com/feedback",
        "project_name_field_id": 1,
        "guidance_url": "http://example.com/guidance",
        "action": "return_home",
    }

    response = submit_form(flask_test_client, f"/applications/create?fund_id={test_fund.fund_id}", new_round_data)
    assert response.request.path == "/dashboard"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_all_applications_page(flask_test_client, seed_dynamic_data):
    response = flask_test_client.get(
        "/applications", follow_redirects=True, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200
    html = response.data.decode("utf-8")

    # Title component availability check
    assert '<h1 class="govuk-heading-l">' in html, "Heading title component is missing"
    assert "Applications" in html, "Heading title is missing"

    # Description component availability check
    assert '<p class="govuk-body">' in html, "Description component is missing"
    assert "View existing applications or create a new one." in html, "Description is missing"

    # Detail component availability check
    assert '<span class="govuk-details__summary-text">' in html, "Detail summary drop down title component is missing"
    assert "Creating a new grant application" in html, "Detail summary drop down title is missing"
    assert "Follow the step-by-step instructions to create a new grant application." in html, (
        "Detail summary description is missing"
    )
    assert '<div class="govuk-details__text">' in html, "Detail summary description component is missing"

    # Button component availability check
    assert "Create new application" in html, "Button text is missing"

    # Table component availability check and data testing
    assert '<thead class="govuk-table__head">' in html, "Table is missing"
    assert '<th scope="col" class="govuk-table__header">Application name</th>' in html, (
        "Application Name header is missing"
    )
    assert '<th scope="col" class="govuk-table__header">Grant</th>' in html, "Grant Name header missing"
    assert "round the first" in html, "Application name is missing"
    assert "funding to improve testing" in html, "Grant name and table component is missing"
    assert "Build application" in html, "Build application is not available and table component is missing"
