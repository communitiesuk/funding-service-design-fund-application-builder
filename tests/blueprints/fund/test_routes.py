import pytest

from app.db.models import Fund
from app.db.models.fund import FundingType
from app.db.queries.fund import get_fund_by_id
from tests.helpers import submit_form


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user")
def test_create_fund(flask_test_client):
    """
    Tests that a fund can be successfully created using the /grants/create route
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
def test_create_fund_with_existing_short_name(flask_test_client):
    """
    Tests that a fund can be successfully created using the /grants/create route
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
    response = submit_form(flask_test_client, "/grants/create", create_data)
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
    response = submit_form(flask_test_client, "/grants/create", create_data)
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert '<a href="#short_name">Short name: Given fund short name already exists.</a>' in html, (
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
def test_create_fund_with_return_home(flask_test_client):
    """Tests that 'Save and return home' action correctly redirects to dashboard after fund creation"""
    create_data = {
        "name_en": "New Fund",
        "title_en": "New Fund Title",
        "description_en": "New Fund Description",
        "welsh_available": "false",
        "short_name": "NF5433",
        "funding_type": FundingType.COMPETITIVE.value,
        "ggis_scheme_reference_number": "G1-SCH-0000092415",
        "action": "return_home",
    }

    response = submit_form(flask_test_client, "/grants/create", create_data)
    assert response.request.path == "/dashboard"


@pytest.mark.usefixtures("set_auth_cookie", "patch_validate_token_rs256_internal_user", "seed_dynamic_data")
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
    assert '<th scope="col" class="govuk-table__header">Grant Name</th>' in html, "Grant Name header is missing"
    assert '<th scope="col" class="govuk-table__header">Description</th>' in html, "Description header missing"
    assert '<th scope="col" class="govuk-table__header">Grant Type</th>' in html, "Grant type header missing"
    assert "New Fund" in html, "Grant name is missing"
    assert "<a class='govuk-link--no-visited-state'" in html, "Grant view link is missing"
    assert '<td class="govuk-table__cell">New Fund Description</td>' in html, "Fund Description is missing"
    assert '<td class="govuk-table__cell">Competitive</td>' in html, "Grant type is missing"

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
    assert f'<h2 class="govuk-heading-l">{test_fund.name_json["en"]}</h2>' in html
    assert (
        f'<a class="govuk-link govuk-link--no-visited-state" href="/grants/{test_fund.fund_id}/edit#name_en">Change'
        f'<span class="govuk-visually-hidden"> Name english</span></a>' in html  # noqa: E501
    )
    assert '<a href="/grants/" class="govuk-back-link">Back</a>' in html

    assert '<dt class="govuk-summary-list__key"> Grant name (Welsh)</dt>' not in html
