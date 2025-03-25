from datetime import datetime
from random import randint
from uuid import uuid4

import pytest
from sqlalchemy.orm import joinedload

from app.db.models import Component, Fund, FundingType, Lizt, Round, Section
from app.db.queries.round import add_round, delete_selected_round, get_round_by_id
from tests.seed_test_data import BASIC_ROUND_INFO


@pytest.mark.seed_config(
    {
        "funds": [
            Fund(
                fund_id=uuid4(),
                name_json={"en": "Test Fund To Create Rounds"},
                title_json={"en": "funding to improve stuff"},
                description_json={"en": "A £10m fund to improve stuff across the devolved nations."},
                welsh_available=False,
                short_name="TFCR1",
                funding_type=FundingType.COMPETITIVE,
                ggis_scheme_reference_number="G1-SCH-0000092415",
            )
        ]
    }
)
def test_add_round(seed_dynamic_data):
    result = add_round(
        Round(
            fund_id=seed_dynamic_data["funds"][0].fund_id,
            audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
            title_json={"en": "test title"},
            short_name=f"Z{randint(0, 99999)}",
            opens=datetime.now(),
            deadline=datetime.now(),
            assessment_start=datetime.now(),
            reminder_date=datetime.now(),
            assessment_deadline=datetime.now(),
            prospectus_link="http://www.google.com",
            privacy_notice_link="http://www.google.com",
            application_reminder_sent=False,
            contact_email="test@test.com",
            instructions_json={},
            feedback_link="http://www.google.com",
            project_name_field_id="12312312312",
            application_guidance_json={},
            guidance_url="http://www.google.com",
            all_uploaded_documents_section_available=False,
            application_fields_download_available=False,
            display_logo_on_pdf_exports=False,
            mark_as_complete_enabled=False,
            is_expression_of_interest=False,
            feedback_survey_config={},
            eligibility_config={},
            eoi_decision_schema={},
        )
    )
    assert result
    assert result.round_id


def test_get_round_by_id_none(flask_test_client, _db):
    with pytest.raises(ValueError) as exc_info:
        get_round_by_id(str(uuid4()))
    assert "not found" in str(exc_info.value)


fund_id = uuid4()


@pytest.mark.seed_config(
    {
        "funds": [
            Fund(
                fund_id=fund_id,
                name_json={"en": "Test Fund 1"},
                title_json={"en": "funding to improve stuff"},
                description_json={"en": "A £10m fund to improve stuff across the devolved nations."},
                welsh_available=False,
                short_name="TFR1",
                funding_type=FundingType.COMPETITIVE,
            )
        ],
        "rounds": [
            Round(
                round_id=uuid4(),
                fund_id=fund_id,
                audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
                title_json={"en": "round the first"},
                short_name="R1",
                opens=datetime.now(),
                deadline=datetime.now(),
                assessment_start=datetime.now(),
                reminder_date=datetime.now(),
                assessment_deadline=datetime.now(),
                prospectus_link="http://www.google.com",
                privacy_notice_link="http://www.google.com",
                application_reminder_sent=False,
                contact_email="test@test.com",
                instructions_json={},
                feedback_link="http://www.google.com",
                project_name_field_id="12312312312",
                application_guidance_json={},
                guidance_url="http://www.google.com",
                all_uploaded_documents_section_available=False,
                application_fields_download_available=False,
                display_logo_on_pdf_exports=False,
                mark_as_complete_enabled=False,
                is_expression_of_interest=False,
                feedback_survey_config=None,
                eligibility_config=None,
                eoi_decision_schema={},
            )
        ],
    }
)
def test_get_round_by_id(seed_dynamic_data):
    result: Round = get_round_by_id(seed_dynamic_data["rounds"][0].round_id)
    assert result.title_json["en"] == "round the first"


def test_base_path_sequence_insert(seed_dynamic_data, _db):
    fund = seed_dynamic_data["funds"][0]
    new_round_1 = Round(
        **BASIC_ROUND_INFO, title_json={"en": "round1"}, round_id=uuid4(), fund_id=fund.fund_id, short_name="R1"
    )
    added_round_1 = add_round(new_round_1)
    assert added_round_1.section_base_path
    new_round_2 = Round(
        **BASIC_ROUND_INFO, title_json={"en": "round2"}, round_id=uuid4(), fund_id=fund.fund_id, short_name="R2"
    )
    added_round_2 = add_round(new_round_2)
    assert added_round_2.section_base_path
    assert added_round_2.section_base_path > added_round_1.section_base_path


def test_delete_application(_db, seed_fund_without_assessment):
    """Test that the delete endpoint redirects application table page"""
    test_round: Round = seed_fund_without_assessment["rounds"][0]
    output: Fund = _db.session.get(
        Fund, test_round.fund_id, options=[joinedload(Fund.rounds).joinedload(Round.sections)]
    )
    assert output is not None, "No values present in the db"
    delete_selected_round(test_round.round_id)
    _db.session.commit()
    output_f = _db.session.get(Fund, test_round.fund_id, options=[joinedload(Fund.rounds).joinedload(Round.sections)])
    assert output_f is not None, "Grant deleted"
    output_r = _db.session.query(Round).all()
    assert not output_r, "Round delete did not happened"
    output_s = _db.session.query(Section).all()
    assert not output_s, "Section delete did not happened"
    output_c = _db.session.query(Component).all()
    assert not output_c, "Component delete did not happened"
    output_l = _db.session.query(Lizt).all()
    assert not output_l, "Lizt delete did not happened"
