from unittest.mock import MagicMock, patch

import pytest
from flask import current_app
from wtforms.validators import ValidationError

from app.blueprints.fund_builder.forms.round import validate_json_field
from app.db.models import Fund, Round
from app.db.models.fund import FundingType
from app.db.queries.fund import get_fund_by_id
from app.db.queries.round import get_round_by_id
from tests.helpers import submit_form


@pytest.fixture
def set_auth_cookie(flask_test_client):
    # This fixture sets the authentication cookie on every test.
    user_token_cookie_name = current_app.config.get("FSD_USER_TOKEN_COOKIE_NAME", "fsd_user_token")
    flask_test_client.set_cookie(key=user_token_cookie_name, value="dummy_jwt_token")
    yield


@pytest.fixture
def patch_validate_token_rs256_internal_user():
    # This fixture patches validate_token_rs256 for all tests automatically.
    with patch("fsd_utils.authentication.decorators.validate_token_rs256") as mock_validate_token_rs256:
        mock_validate_token_rs256.return_value = {
            "accountId": "test-account-id",
            "roles": [],
            "email": "test@communities.gov.uk",
        }
        yield mock_validate_token_rs256


@pytest.fixture
def patch_validate_token_rs256_external_user():
    # This fixture patches validate_token_rs256 for all tests automatically.
    with patch("fsd_utils.authentication.decorators.validate_token_rs256") as mock_validate_token_rs256:
        mock_validate_token_rs256.return_value = {
            "accountId": "test-account-id",
            "roles": [],
            "email": "test@gmail.com",
        }
        yield mock_validate_token_rs256


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_fund(flask_test_client):
    """
    Tests that a fund can be successfully created using the /fund route
    Verifies that the created fund has the correct attributes
    """
    create_data = {
        "name_en": "New Fund",
        "title_en": "New Fund Title",
        "description_en": "New Fund Description",
        "welsh_available": "false",
        "short_name": "NF5432",
        "funding_type": FundingType.COMPETITIVE.value,
        "ggis_scheme_reference_number": "G1-SCH-0000092415",
    }

    response = submit_form(flask_test_client, "/fund", create_data)
    assert response.status_code == 200
    created_fund = Fund.query.filter_by(short_name="NF5432").first()
    assert created_fund is not None
    for key, value in create_data.items():
        if key == "csrf_token":
            continue
        if key.endswith("_en"):
            assert created_fund.__getattribute__(key[:-3] + "_json")["en"] == value
        elif key == "welsh_available":
            assert created_fund.welsh_available is False
        elif key == "funding_type":
            assert created_fund.funding_type.value == value
        elif key == "ggis_scheme_reference_number":
            assert created_fund.ggis_scheme_reference_number == value
        else:
            assert created_fund.__getattribute__(key) == value


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_fund_with_existing_short_name(flask_test_client):
    """
    Tests that a fund can be successfully created using the /fund route
    Verifies that the created fund has the correct attributes
    """
    create_data = {
        "name_en": "New Fund 2",
        "title_en": "New Fund Title 2",
        "description_en": "New Fund Description 2",
        "welsh_available": "false",
        "short_name": "SMP1",
        "funding_type": FundingType.COMPETITIVE.value,
        "ggis_scheme_reference_number": "G1-SCH-0000092415",
    }
    response = submit_form(flask_test_client, "/fund", create_data)
    assert response.status_code == 200
    create_data = {
        "name_en": "New Fund 3",
        "title_en": "New Fund Title 3",
        "description_en": "New Fund Description 3",
        "welsh_available": "false",
        "short_name": "SMP1",
        "funding_type": FundingType.COMPETITIVE.value,
        "ggis_scheme_reference_number": "G1-SCH-0000092415",
    }
    response = submit_form(flask_test_client, "/fund", create_data)
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert (
        '<a href="#short_name">Short name: Given fund short name already exists.</a>' in html
    ), "Not having the fund short name already exists error"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_update_fund(flask_test_client, seed_dynamic_data):
    """
    Tests that a fund can be successfully updated using the /fund/<fund_id> route
    Verifies that the updated fund has the correct attributes
    """
    update_data = {
        "name_en": "Updated Fund",
        "title_en": "Updated Fund Title",
        "description_en": "Updated Fund Description",
        "welsh_available": "true",
        "short_name": "UF1234",
        "submit": "Submit",
        "funding_type": "EOI",
        "ggis_scheme_reference_number": "G3-SCH-0000092414",
    }

    test_fund = seed_dynamic_data["funds"][0]
    response = submit_form(flask_test_client, f"/fund/{test_fund.fund_id}", update_data)
    assert response.status_code == 200

    updated_fund = get_fund_by_id(test_fund.fund_id)
    for key, value in update_data.items():
        if key == "csrf_token":
            continue
        if key.endswith("_en"):
            assert updated_fund.__getattribute__(key[:-3] + "_json")["en"] == value
        elif key == "welsh_available":
            assert updated_fund.welsh_available is True
        elif key == "funding_type":
            assert updated_fund.funding_type.value == value
        elif key != "submit":
            assert updated_fund.__getattribute__(key) == value


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_round_with_existing_short_name(flask_test_client, seed_dynamic_data):
    """
    Tests that a round can be successfully created using the /round route
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
        "submit": "Submit",
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

    # Test works fine with first round
    response = submit_form(flask_test_client, "/round", new_round_data)
    assert response.status_code == 200
    assert error_html not in response.data.decode("utf-8"), "Error HTML found in response"

    # Test works fine with second round but with different short name
    new_round_data = {**new_round_data, "short_name": "NR1234"}
    response = submit_form(flask_test_client, "/round", new_round_data)
    assert response.status_code == 200
    assert error_html not in response.data.decode("utf-8"), "Error HTML found in response"

    # Test doesn't work with third round with same short name as firsrt
    new_round_data = {**new_round_data, "short_name": "NR123"}
    response = submit_form(flask_test_client, "/round", new_round_data)
    assert response.status_code == 200
    assert error_html in response.data.decode("utf-8"), "Error HTML not found in response"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_new_round(flask_test_client, seed_dynamic_data):
    """
    Tests that a round can be successfully created using the /round route
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
        "submit": "Submit",
        "contact_phone": "1234567890",
        "contact_textphone": "0987654321",
        "support_times": "9am - 5pm",
        "support_days": "Monday to Friday",
        "feedback_link": "http://example.com/feedback",
        "project_name_field_id": 1,
        "guidance_url": "http://example.com/guidance",
    }

    response = submit_form(flask_test_client, "/round", new_round_data)
    assert response.status_code == 200

    new_round = Round.query.filter_by(short_name="NR123").first()
    assert new_round is not None
    assert new_round.title_json["en"] == "New Round"
    assert new_round.short_name == "NR123"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_update_existing_round(flask_test_client, seed_dynamic_data):
    """
    Tests that a round can be successfully updated using the /round/<round_id> route
    Verifies that the updated round has the correct attributes
    """
    update_round_data = {
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
        "submit": "Submit",
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
    response = submit_form(flask_test_client, f"/round/{test_round.round_id}", update_round_data)
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


@pytest.mark.parametrize("input_json_string", [(None), (""), ("{}"), (""), ("{}"), ('{"1":"2"}')])
def test_validate_json_input_valid(input_json_string):
    field = MagicMock()
    field.data = input_json_string
    validate_json_field(None, field)


@pytest.mark.parametrize(
    "input_json_string, exp_error_msg",
    [
        ('{"1":', "Expecting value: line 1 column 6 (char 5)]"),
        ('{"1":"quotes not closed}', "Unterminated string starting at: line 1 column 6 (char 5)"),
    ],
)
def test_validate_json_input_invalid(input_json_string, exp_error_msg):
    field = MagicMock()
    field.data = input_json_string
    with pytest.raises(ValidationError) as error:
        validate_json_field(None, field)
    assert exp_error_msg in str(error)


def test_index_redirects_to_login_for_unauthenticated_user(flask_test_client):
    """
    Tests that unauthenticated users are redirected to the login page when trying to access the index route.
    """
    response = flask_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/login"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_index_redirects_to_dashboard_for_authenticated_user(flask_test_client):
    """
    Tests that authenticated users are redirected to the dashboard when trying to access the index route.
    """
    response = flask_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/dashboard"


def test_login_renders_for_unauthenticated_user(flask_test_client):
    """
    Tests that the login page renders correctly for unauthenticated users.
    """
    response = flask_test_client.get("/login")
    assert response.status_code == 200
    assert b"Sign in to use FAB" in response.data


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_dashboard_renders_for_internal_user(flask_test_client):
    """
    Tests that authenticated internal users can access the dashboard.
    """
    response = flask_test_client.get("/dashboard")
    assert response.status_code == 200
    assert b"What do you want to do?" in response.data


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_external_user")
def test_dashboard_forbidden_for_external_user(flask_test_client):
    """
    Tests that authenticated external users are forbidden from accessing the dashboard.
    """
    response = flask_test_client.get("/dashboard")
    assert response.status_code == 403
    assert b"You do not have permission to access this page" in response.data
