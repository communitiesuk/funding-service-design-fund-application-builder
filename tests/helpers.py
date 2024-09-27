from datetime import datetime
from uuid import uuid4

from sqlalchemy import select

from app.db import db
from app.db.models import Fund
from app.db.models import Organisation
from app.db.models import Round
from app.db.queries.fund import add_fund
from app.db.queries.fund import add_organisation
from app.db.queries.round import add_round


def get_round_by_title(title: str) -> Round:
    """
    Retrieves a Round object by its title

    Args:
        title: The title of the round to retrieve

    Returns:
        The Round object with the given title

    Raises:
        ValueError: If no Round with the given title is found
    """
    stmt = select(Round).where(Round.title_json["en"].astext == title)
    round = db.session.scalars(stmt).first()
    if not round:
        raise ValueError(f"Round with title '{title}' not found")
    return round


def create_test_organisation(flask_test_client):
    """
    Creates a test Organisation and persists it to the database.

    Args:
        flask_test_client: The test client to use for the request

    Returns:
        The Organisation object created
    """
    return add_organisation(
        Organisation(
            name=f"test_org_{uuid4().hex[:8]}",
            short_name=f"X{uuid4().hex[:8]}",
            logo_uri="http://www.example.com",
            funds=[],
        )
    )


def create_test_fund(flask_test_client, organisation):
    """
    Creates a test Fund and persists it to the database.

    Args:
        flask_test_client: The test client to use for the request
        organisation: The Organisation object to use as the owner of the fund

    Returns:
        The Fund object created
    """
    return add_fund(
        Fund(
            name_json={"en": "Test Fund"},
            title_json={"en": "Test Fund Title"},
            description_json={"en": "Test Fund Description"},
            welsh_available=False,
            short_name=f"F{uuid4().hex[:8]}",
            owner_organisation_id=organisation.organisation_id,
        )
    )


def create_test_round(flask_test_client, fund):
    """
    Creates a test Round and persists it to the database.

    Args:
        flask_test_client: The test client to use for the request
        fund: The Fund object to use as the owner of the round

    Returns:
        The Round object created
    """
    return add_round(
        Round(
            fund_id=fund.fund_id,
            title_json={"en": "Test Round"},
            short_name=f"R{uuid4().hex[:8]}",
            opens=datetime.now(),
            deadline=datetime.now(),
            assessment_start=datetime.now(),
            reminder_date=datetime.now(),
            assessment_deadline=datetime.now(),
            prospectus_link="http://www.example.com",
            privacy_notice_link="http://www.example.com",
            contact_email="test@example.com",
            contact_phone="1234567890",
            contact_textphone="0987654321",
            support_times="9am - 5pm",
            support_days="Monday to Friday",
            feedback_link="http://example.com/feedback",
            project_name_field_id=1,
            guidance_url="http://example.com/guidance",
            eligibility_config={"has_eligibility": "false"},
            eoi_decision_schema={"en": "eoi_decision_schema", "cy": ""},
            contact_us_banner_json={"en": "contact_us_banner", "cy": ""},
            instructions_json={"en": "instructions", "cy": ""},
            application_guidance_json={"en": "application_guidance", "cy": ""},
        )
    )


def get_csrf_token(response):
    """
    Extracts the CSRF token from the given response.

    Args:
        response: The response to extract the CSRF token from

    Returns:
        The CSRF token
    """
    return response.data.decode().split('name="csrf_token" type="hidden" value="')[1].split('"')[0]


def submit_form(flask_test_client, url, data):
    """
    Submits a form given a flask test client, url, and the form data.

    Args:
        flask_test_client: The flask test client to use.
        url: The url of the form to submit.
        data: The data to submit on the form.

    Returns:
        The response from submitting the form.
    """
    response = flask_test_client.get(url)
    csrf_token = get_csrf_token(response)
    data["csrf_token"] = csrf_token
    return flask_test_client.post(
        url, data=data, follow_redirects=True, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
