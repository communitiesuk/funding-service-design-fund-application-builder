import pytest
from bs4 import BeautifulSoup
from flask import g

from app.db.models import Fund
from app.db.models.fund import FundingType
from app.db.queries.fund import get_fund_by_id
from tests.helpers import submit_form


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_fund(flask_test_client, seed_dynamic_data):
    """
    Tests that a fund can be successfully created using the /grants/create route
    Verifies that the created fund has the correct attributes
    """
    create_data = {
        "name_en": "New Fund",
        "title_en": "New Fund Title",
        "description_en": "New fund description",
        "welsh_available": "false",
        "short_name": "NF5432",
        "funding_type": FundingType.COMPETITIVE.value,
        "ggis_scheme_reference_number": "G1-SCH-0000092415",
    }

    response = submit_form(flask_test_client, "/grants/create", create_data)
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
def test_create_fund_with_existing_short_name(flask_test_client, seed_dynamic_data):
    """
    Tests that a fund can be successfully created using the /grants/create route
    Verifies that the created fund has the correct attributes
    """
    create_data = {
        "name_en": "New Fund 2",
        "title_en": "New Fund Title 2",
        "description_en": "New fund description 2",
        "welsh_available": "false",
        "short_name": "SMP1",
        "funding_type": FundingType.COMPETITIVE.value,
        "ggis_scheme_reference_number": "G1-SCH-0000092415",
    }
    response = submit_form(flask_test_client, "/grants/create", create_data)
    assert response.status_code == 200
    create_data = {
        "name_en": "New Fund 3",
        "title_en": "New Fund Title 3",
        "description_en": "New fund description 3",
        "welsh_available": "false",
        "short_name": "SMP1",
        "funding_type": FundingType.COMPETITIVE.value,
        "ggis_scheme_reference_number": "G1-SCH-0000092415",
    }
    response = submit_form(flask_test_client, "/grants/create", create_data)
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert '<a href="#short_name">Grant short name must be unique</a>' in html, (
        "Not having the fund short name already exists error"
    )


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_update_fund(flask_test_client, seed_dynamic_data):
    """
    Tests that a fund can be successfully updated using the /grants/<fund_id> route
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
    response = submit_form(flask_test_client, f"/grants/{test_fund.fund_id}/edit", update_data)
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
def test_update_fund_and_return_home(flask_test_client, seed_dynamic_data):
    """Tests that 'Save and return home' action correctly redirects to dashboard after fund update"""
    test_fund = seed_dynamic_data["funds"][0]
    flask_test_client.get(f"/grants/{test_fund.fund_id}/edit")
    with flask_test_client.session_transaction():
        update_data = {
            "name_en": "Updated Fund",
            "title_en": "Updated Fund Title",
            "description_en": "Updated Fund Description",
            "welsh_available": "true",
            "short_name": "UF1234",
            "submit": "Submit",
            "funding_type": "EOI",
            "ggis_scheme_reference_number": "G3-SCH-0000092414",
            "save_and_return_home": True,
            "csrf_token": g.csrf_token,
        }
        response = flask_test_client.post(
            f"/grants/{test_fund.fund_id}/edit",
            data=update_data,
            follow_redirects=True,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    assert response.request.path == "/dashboard"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_update_fund_and_return_fund_details(flask_test_client, seed_dynamic_data):
    """Tests that 'Save and continue' action correctly redirects to dashboard after fund update"""
    test_fund = seed_dynamic_data["funds"][0]
    flask_test_client.get(f"/grants/{test_fund.fund_id}/edit")
    with flask_test_client.session_transaction():
        update_data = {
            "name_en": "Updated Fund",
            "title_en": "Updated Fund Title",
            "description_en": "Updated Fund Description",
            "welsh_available": "true",
            "short_name": "UF1234",
            "submit": "Submit",
            "funding_type": "EOI",
            "ggis_scheme_reference_number": "G3-SCH-0000092414",
            "save_and_continue": True,
            "csrf_token": g.csrf_token,
        }
        response = flask_test_client.post(
            f"/grants/{test_fund.fund_id}/edit",
            data=update_data,
            follow_redirects=True,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    assert response.request.path == f"/grants/{test_fund.fund_id}"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_update_fund_and_return_round_details(flask_test_client, seed_dynamic_data):
    """Tests that 'Save and continue' action correctly redirects to dashboard after fund update"""
    test_fund = seed_dynamic_data["funds"][0]
    test_round = seed_dynamic_data["rounds"][0]
    flask_test_client.get(f"/grants/{test_fund.fund_id}/edit")
    with flask_test_client.session_transaction():
        update_data = {
            "name_en": "Updated Fund",
            "title_en": "Updated Fund Title",
            "description_en": "Updated Fund Description",
            "welsh_available": "true",
            "short_name": "UF1234",
            "submit": "Submit",
            "funding_type": "EOI",
            "ggis_scheme_reference_number": "G3-SCH-0000092414",
            "save_and_continue": True,
            "csrf_token": g.csrf_token,
        }
        response = flask_test_client.post(
            f"/grants/{test_fund.fund_id}/edit?actions=view_application&round_id={test_round.round_id}",
            data=update_data,
            follow_redirects=True,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    assert response.request.path == f"/rounds/{test_round.round_id}"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_fund_with_return_home(flask_test_client):
    """Tests that 'Save and return home' action correctly redirects to dashboard after fund creation"""
    flask_test_client.get("/grants/create")
    create_data = {
        "name_en": "New Fund",
        "title_en": "New Fund Title",
        "description_en": "New fund description",
        "welsh_available": "false",
        "short_name": "NF5433",
        "funding_type": FundingType.COMPETITIVE.value,
        "ggis_scheme_reference_number": "G1-SCH-0000092415",
        "save_and_return_home": True,
        "csrf_token": g.csrf_token,
    }
    with flask_test_client.session_transaction():
        response = flask_test_client.post(
            "/grants/create",
            data=create_data,
            follow_redirects=True,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    assert response.request.path == "/dashboard"
    soup = BeautifulSoup(response.data, "html.parser")
    notification = soup.find("h3", {"class": "govuk-notification-banner__heading"})
    assert notification.text.strip() == "New grant added successfully"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user", "clean_db")
def test_create_fund_from_grant_details(flask_test_client, seed_dynamic_data):
    """Tests that 'Save and continue' action correctly redirects to grants list after fund creation"""
    flask_test_client.get("/grants/create?actions=grants_table")
    with flask_test_client.session_transaction():
        create_data = {
            "name_en": "New Fund",
            "title_en": "New Fund Title",
            "description_en": "New fund description",
            "welsh_available": "false",
            "short_name": "NF5433",
            "funding_type": FundingType.COMPETITIVE.value,
            "ggis_scheme_reference_number": "G1-SCH-0000092415",
            "save_and_continue": True,
            "csrf_token": g.csrf_token,
        }
        response = flask_test_client.post(
            "/grants/create?actions=grants_table",
            data=create_data,
            follow_redirects=True,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.request.path == "/grants/"
        soup = BeautifulSoup(response.data, "html.parser")
        notification = soup.find("h3", {"class": "govuk-notification-banner__heading"})
        assert notification.text.strip() == "New grant added successfully"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user", "clean_db")
def test_create_fund_from_select_grant(flask_test_client):
    """Tests that 'Save and continue' action correctly redirects to round creation after fund creation
    when add grant is submitted from select grant page"""
    flask_test_client.get("/grants/create")
    create_data = {
        "name_en": "New Fund",
        "title_en": "New Fund Title",
        "description_en": "New fund description",
        "welsh_available": "false",
        "short_name": "NF5433",
        "funding_type": FundingType.COMPETITIVE.value,
        "ggis_scheme_reference_number": "G1-SCH-0000092415",
        "save_and_continue": True,
        "csrf_token": g.csrf_token,
    }
    with flask_test_client.session_transaction():
        response = flask_test_client.post(
            "/grants/create?actions=select_grant",
            data=create_data,
            follow_redirects=True,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    assert response.request.path == "/rounds/create"
    soup = BeautifulSoup(response.data, "html.parser")
    notification = soup.find("h3", {"class": "govuk-notification-banner__heading"})
    assert notification.text.strip() == "New grant added successfully"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_view_all_funds(flask_test_client, seed_dynamic_data):
    response = flask_test_client.get(
        "/grants/", follow_redirects=True, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200
    html = response.data.decode("utf-8")
    # Title component availability check
    assert '<h1 class="govuk-heading-l">' in html, "Heading title component is missing"
    assert "Grants" in html, "Heading title is missing"

    # Description component availability check
    assert '<p class="govuk-body">' in html, "Description component is missing"
    assert "View all existing grants or add a new grant." in html, "Description is missing"

    # Button component availability check
    assert "Add new grant" in html, "Button text is missing"

    # Table component availability check
    assert '<thead class="govuk-table__head">' in html, "Table is missing"
    assert '<th scope="col" class="govuk-table__header">Grant name</th>' in html, "Grant name header is missing"
    assert '<th scope="col" class="govuk-table__header">Description</th>' in html, "Description header missing"
    assert '<th scope="col" class="govuk-table__header">Grant type</th>' in html, "Grant type header missing"
    assert "New fund" in html, "Grant name is missing"
    assert "New fund description" in html, "Fund description is missing"
    assert "Competitive" in html, "Grant type is missing"

    # fetch test data and check the link to grant details link
    test_fund = seed_dynamic_data["funds"][0]
    assert f"/grants/{test_fund.fund_id}" in html


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_view_fund_details(flask_test_client, seed_dynamic_data):
    """
    Test to check grant detail route is working as expected.
    and verify the grant details template is rendered as expected.
    """
    invalid_fund_id = "123e4567-e89b-12d3-a456-426614174000"
    with pytest.raises(ValueError, match=f"Fund with id {invalid_fund_id} not found"):
        flask_test_client.get(f"/grants/{invalid_fund_id}", follow_redirects=True)

    test_fund = seed_dynamic_data["funds"][0]
    response = flask_test_client.get(f"/grants/{test_fund.fund_id}", follow_redirects=True)
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert f'<h1 class="govuk-heading-l">{test_fund.name_json["en"]}</h1>' in html
    assert (
        f'<a class="govuk-link govuk-link--no-visited-state" href="/grants/{test_fund.fund_id}/edit#name_en">Change'
        f'<span class="govuk-visually-hidden"> Name english</span></a>' in html  # noqa: E501
    )
    assert '<a href="/grants/" class="govuk-back-link">Back</a>' in html

    assert '<dt class="govuk-summary-list__key"> Grant name (Welsh)</dt>' not in html
