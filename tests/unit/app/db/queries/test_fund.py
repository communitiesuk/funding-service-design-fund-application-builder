from random import randint
from uuid import uuid4

import pytest
from sqlalchemy.orm import joinedload

from app.db.models import Round, Section
from app.db.models.fund import Fund, FundingType, Organisation
from app.db.queries.fund import add_fund, add_organisation, delete_selected_fund, get_all_funds, get_fund_by_id


def test_add_organisation(flask_test_client, _db, clear_test_data):
    o = Organisation(
        name="test_org_1",
        short_name=f"X{randint(0, 99999)}",
        logo_uri="http://www.google.com",
        funds=[],
    )
    result = add_organisation(o)
    assert result
    assert result.organisation_id


def test_add_fund(flask_test_client, _db, clear_test_data):
    o = add_organisation(
        Organisation(
            name="test_org_2",
            short_name=f"X{randint(0, 99999)}",
            logo_uri="http://www.google.com",
            funds=[],
        )
    )
    f = Fund(
        name_json={"en": "hello"},
        title_json={"en": "longer hello"},
        description_json={"en": "reeeaaaaallly loooooooog helloooooooooo"},
        welsh_available=False,
        short_name=f"X{randint(0, 99999)}",
        owner_organisation_id=o.organisation_id,
        funding_type=FundingType.COMPETITIVE,
        ggis_scheme_reference_number="G2-SCH-0000092414",
    )
    result = add_fund(f)
    assert result
    assert result.fund_id
    assert result.ggis_scheme_reference_number


def test_get_all_funds(flask_test_client, _db, seed_dynamic_data):
    results = get_all_funds()
    assert results
    assert results[0].fund_id


@pytest.mark.seed_config(
    {
        "funds": [
            Fund(
                fund_id=uuid4(),
                name_json={"en": "Test Fund 1"},
                title_json={"en": "funding to improve stuff"},
                description_json={"en": "A £10m fund to improve stuff across the devolved nations."},
                welsh_available=False,
                short_name="TF1",
                funding_type=FundingType.COMPETITIVE,
                ggis_scheme_reference_number="G2-SCH-0000092414",
            )
        ]
    }
)
def test_get_fund_by_id(seed_dynamic_data):
    result: Fund = get_fund_by_id(seed_dynamic_data["funds"][0].fund_id)
    assert result
    assert result.name_json["en"] == "Test Fund 1"
    assert result.ggis_scheme_reference_number == "G2-SCH-0000092414"


def test_get_fund_by_id_none(flask_test_client, _db):
    with pytest.raises(ValueError) as exc_info:
        get_fund_by_id(str(uuid4()))
    assert "not found" in str(exc_info.value)


def test_delete_grant(_db, seed_fund_without_assessment):
    """Test that the delete endpoint redirects to grant table page"""
    test_fund: Fund = seed_fund_without_assessment["funds"][0]
    output: Fund = _db.session.get(
        Fund, test_fund.fund_id, options=[joinedload(Fund.rounds).joinedload(Round.sections)]
    )
    assert output is not None, "No values present in the db"
    delete_selected_fund(test_fund.fund_id)
    _db.session.commit()
    output_f = _db.session.get(Fund, test_fund.fund_id, options=[joinedload(Fund.rounds).joinedload(Round.sections)])
    assert output_f is None, "Grant delete did not happened"
    output_r = _db.session.query(Round).all()
    assert not output_r, "Round delete did not happened"
    output_s = _db.session.query(Section).all()
    assert not output_s, "Section delete did not happened"
