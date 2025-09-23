import uuid
from datetime import datetime

import pytest
from bs4 import BeautifulSoup
from flask import g, url_for

from app.db.models import Fund, FundingType, Round
from app.db.queries.round import get_round_by_id
from app.shared.form_store_api import PublishedFormResponse
from tests.helpers import submit_form

radio_fields = {
    "application_fields_download_available": "false",
    "display_logo_on_pdf_exports": "false",
    "mark_as_complete_enabled": "false",
    "is_expression_of_interest": "false",
    "has_feedback_survey": "false",
    "is_feedback_survey_optional": "false",
    "has_research_survey": "false",
    "is_research_survey_optional": "false",
    "eligibility_config": "false",
}

round_data_info = {
    "opens": ["01", "10", "2024", "09", "00"],
    "deadline": ["01", "12", "2024", "17", "00"],
    "assessment_start": ["02", "12", "2024", "09", "00"],
    "reminder_date": ["15", "11", "2024", "09", "00"],
    "assessment_deadline": ["15", "12", "2024", "17", "00"],
    "prospectus_link": "https://example.com/prospectus",
    "privacy_notice_link": "https://example.com/privacy",
    "contact_email": "contact@example.com",
    "feedback_link": "https://example.com/feedback",
    "project_name_field_id": 1,
    "guidance_url": "https://example.com/guidance",
    **radio_fields,
}


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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

    error_html = '<a href="#short_name">Application round short name already exists for this grant</a>'
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_create_round_with_invalid_eoi_schema_json(flask_test_client, seed_dynamic_data):
    """
    Tests for rounds/create route verifies that the created round has the correct attributes
    """
    test_fund = seed_dynamic_data["funds"][0]
    new_round_data = {
        "fund_id": test_fund.fund_id,
        "title_en": "New Round",
        "short_name": "test123",
        "save_and_return_home": True,
        "eoi_decision_schema_en": "asdasd",
        **round_data_info,
    }

    error_html = "Content is not valid JSON. Underlying error"
    url = f"/rounds/create?fund_id={test_fund.fund_id}"

    # Test works fine with first round
    response = submit_form(flask_test_client, url, new_round_data)
    assert response.status_code == 200
    assert error_html in response.data.decode("utf-8"), "No errors found in response"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_update_existing_round_check_eoi_schema_optional_value(flask_test_client, seed_dynamic_data):
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
    rows = soup.find_all("div", class_="govuk-summary-list__row")
    for row in rows:
        key = row.find("dt", class_="govuk-summary-list__key").text.strip()
        if key == "Expression of interest decision schema":
            break
    # Extract the corresponding value (the text inside the <dd> tag)
    eoi_schema = row.find("dd", class_="govuk-summary-list__value").text.strip()
    assert eoi_schema == "Not provided"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_all_applications_page(flask_test_client, seed_dynamic_data):
    response = flask_test_client.get("/rounds", follow_redirects=True)

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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_clone_round(flask_test_client, seed_dynamic_data, mocker):
    """
    Test to check round detail route is working as expected.
    and verify the round details template is rendered as expected.
    """
    mock_api_service = mocker.Mock()
    mock_api_service.get_published_form.return_value = PublishedFormResponse(
        id="test-form-id",
        url_path="test-form-path",
        display_name="Test Form",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
        published_at="2024-01-01T00:00:00Z",
        is_published=True,
        published_json={"pages": []},
        hash="test-hash"
    )
    mocker.patch("app.db.queries.application.FormStoreAPIService", return_value=mock_api_service)
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


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_round_search_functionality(flask_test_client, _db):
    test_fund = Fund(
        name_json={"en": "Test Fund For Round Search"},
        title_json={"en": "Test Fund Title"},
        description_json={"en": "Test fund description"},
        welsh_available=False,
        short_name=f"TFR-{datetime.now().strftime('%H%M%S')}",  # Ensure uniqueness
        audit_info={"user": "test_user", "timestamp": datetime.now().isoformat(), "action": "create"},
        funding_type=FundingType.COMPETITIVE,
    )
    _db.session.add(test_fund)
    _db.session.flush()

    test_round = Round(
        round_id=uuid.uuid4(),
        fund_id=test_fund.fund_id,
        title_json={"en": "Special Test Round ABC456"},
        short_name=f"STR-{datetime.now().strftime('%H%M%S')}",  # Ensure uniqueness
        prospectus_link="https://example.com/prospectus",
        privacy_notice_link="https://example.com/privacy",
        project_name_field_id="test_field_id",
        status="In progress",
    )
    _db.session.add(test_round)
    _db.session.commit()

    expected_application_name = f"Apply for {test_fund.title_json['en']}"

    try:
        response = flask_test_client.get("/rounds/")
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, "html.parser")

        # Helper function to get application names from table (first column)
        def get_application_names(soup):
            return [link.text.strip() for link in soup.select("tbody tr td:first-child a")]

        # Find label and button
        search_label = soup.find("label", {"for": "search"})
        assert search_label is not None
        assert "Search applications" in search_label.text

        search_button = soup.find("button", {"class": "govuk-button--success"})
        assert search_button is not None
        assert "Search" in search_button.text

        # Test 1: No search term - should show all results including our test round
        response = flask_test_client.get("/rounds/")
        soup = BeautifulSoup(response.data, "html.parser")
        rows = soup.select("tbody tr")
        assert len(rows) > 0
        application_names = get_application_names(soup)
        assert expected_application_name in application_names

        # Test 2: Search for prefix of fund title
        response = flask_test_client.get("/rounds/?search=Apply%20for%20Test")
        soup = BeautifulSoup(response.data, "html.parser")
        assert soup.find("input", {"id": "search"}).get("value") == "Apply for Test"
        assert soup.find("a", string=lambda text: text and "Clear search" in text)
        rows = soup.select("tbody tr")
        assert len(rows) > 0
        application_names = get_application_names(soup)
        assert expected_application_name in application_names

        # Test 3: Search for substring of fund title
        response = flask_test_client.get("/rounds/?search=Fund%20Title")
        soup = BeautifulSoup(response.data, "html.parser")
        rows = soup.select("tbody tr")
        assert len(rows) > 0
        application_names = get_application_names(soup)
        assert expected_application_name in application_names

        # Test 4: Search with different case
        response = flask_test_client.get("/rounds/?search=apply%20for%20test")
        soup = BeautifulSoup(response.data, "html.parser")
        rows = soup.select("tbody tr")
        assert len(rows) > 0
        application_names = get_application_names(soup)
        assert expected_application_name in application_names

        # Test 5: No matches
        response = flask_test_client.get("/rounds/?search=No%20Matching%20Application%20Here")
        soup = BeautifulSoup(response.data, "html.parser")
        rows = soup.select("tbody tr")
        assert len(rows) == 0

    finally:
        # Clean up test data
        _db.session.delete(test_round)
        _db.session.delete(test_fund)
        _db.session.commit()


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_create_round_with_application_close_date_before_open_date(flask_test_client, seed_dynamic_data):
    """
    Tests that a round can be successfully created using the /rounds/create route
    Verifies that the created round has the correct attributes
    """
    round_data_info = {
        "opens": ["01", "10", "2024", "09", "00"],
        "deadline": ["01", "09", "2024", "17", "00"],
        "assessment_start": ["02", "12", "2024", "09", "00"],
        "reminder_date": ["15", "11", "2024", "09", "00"],
        "assessment_deadline": ["12", "12", "2024", "17", "00"],
        "prospectus_link": "https://example.com/prospectus",
        "privacy_notice_link": "https://example.com/privacy",
        "contact_email": "contact@example.com",
        "feedback_link": "https://example.com/feedback",
        "project_name_field_id": 1,
        "guidance_url": "https://example.com/guidance",
        **radio_fields,
    }
    test_fund = seed_dynamic_data["funds"][0]
    new_round_data = {
        "fund_id": test_fund.fund_id,
        "title_en": "New Round",
        "short_name": "NR123",
        "save_and_return_home": True,
        **round_data_info,
    }
    url = f"/rounds/create?fund_id={test_fund.fund_id}"

    response = submit_form(flask_test_client, url, new_round_data)
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")
    expected = [
        "The date the application round opens must be before the date the application closes",
        "The date the application round closes must be after the date the application opens",
    ]
    error_messages = [li.get_text(strip=True) for li in soup.select(".govuk-error-summary__list li")]

    assert error_messages == expected


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_allowed_domain_user")
def test_create_round_with_assessment_close_date_before_open_date(flask_test_client, seed_dynamic_data):
    """
    Tests that a round can be successfully created using the /rounds/create route
    Verifies that the created round has the correct attributes
    """
    round_data_info = {
        "opens": ["01", "10", "2024", "09", "00"],
        "deadline": ["11", "10", "2024", "17", "00"],
        "assessment_start": ["02", "12", "2024", "09", "00"],
        "reminder_date": ["15", "11", "2024", "09", "00"],
        "assessment_deadline": ["9", "09", "2024", "17", "00"],
        "prospectus_link": "https://example.com/prospectus",
        "privacy_notice_link": "https://example.com/privacy",
        "contact_email": "contact@example.com",
        "feedback_link": "https://example.com/feedback",
        "project_name_field_id": 1,
        "guidance_url": "https://example.com/guidance",
        **radio_fields,
    }
    test_fund = seed_dynamic_data["funds"][0]
    new_round_data = {
        "fund_id": test_fund.fund_id,
        "title_en": "New Round",
        "short_name": "NR123",
        "save_and_return_home": True,
        **round_data_info,
    }
    url = f"/rounds/create?fund_id={test_fund.fund_id}"

    response = submit_form(flask_test_client, url, new_round_data)
    assert response.status_code == 200

    soup = BeautifulSoup(response.data, "html.parser")
    expected = [
        "The date the assessment opens must be before the date the assessment closes",
        "The date the assessment closes must be after the date the assessment opens",
    ]
    error_messages = [li.get_text(strip=True) for li in soup.select(".govuk-error-summary__list li")]
    assert error_messages == expected
