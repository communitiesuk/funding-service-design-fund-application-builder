from datetime import datetime
from random import randint
from uuid import uuid4

from app.db.models import (
    Form,
    Fund,
    Organisation,
    Round,
    Section,
)
from app.db.models.fund import FundingType

# NOSONAR Ignore since this data is related to unit tests
BASIC_FUND_INFO = {
    "name_json": {"en": "Unit Test Fund"},
    "title_json": {"en": "funding to improve testing"},
    "description_json": {"en": "A £10m fund to improve testing across the devolved nations."},
    "welsh_available": False,
    "owner_organisation_id": None,
    "funding_type": FundingType.COMPETITIVE,
    "ggis_scheme_reference_number": "G2-SCH-0000092414",
}

# NOSONAR Ignore since this data is related to unit tests
BASIC_ROUND_INFO = {
    "audit_info": {"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
    "opens": "2024-10-01T11:59:00",
    "deadline": "2024-10-31T11:59:00",
    "assessment_start": "2024-10-01T11:59:00",
    "reminder_date": "2024-10-20T11:59:00",
    "assessment_deadline": "2024-11-30T11:59:00",
    "project_name_field_id": 1,
    "prospectus_link": "https://www.gov.uk/government/organisations/ministry-of-housing-communities-local-government",
    "privacy_notice_link": "https://www.gov.uk/government/organisations/"
    "ministry-of-housing-communities-local-government",
    "contact_email": "help@fab.gov.uk",
    "instructions_json": {},
    "feedback_link": "https://www.gov.uk/government/organisations/ministry-of-housing-communities-local-government",
    "application_guidance_json": {
        "en": "You can view <a href='{all_questions_url}'>all the questions we will ask you</a> if you want to."
    },
    "guidance_url": "https://www.gov.uk/government/organisations/ministry-of-housing-communities-local-government",
    "all_uploaded_documents_section_available": False,
    "application_fields_download_available": False,
    "display_logo_on_pdf_exports": False,
    "mark_as_complete_enabled": False,
    "is_expression_of_interest": False,
    "eoi_decision_schema": {},
    "feedback_survey_config": {
        "has_feedback_survey": False,
        "has_section_feedback": False,
        "has_research_survey": False,
        "is_feedback_survey_optional": False,
        "is_section_feedback_optional": False,
        "is_research_survey_optional": False,
    },
    "eligibility_config": {"has_eligibility": False},
    "status": "In progress",
}

page_one_id = uuid4()
page_two_id = uuid4()
page_three_id = uuid4()
page_four_id = uuid4()
page_five_id = uuid4()
alt_page_id = uuid4()


ABOUT_YOUR_ORG_FORM_JSON = {
    "startPage": "/organisation-name",
    "pages": [
        {
            "path": "/organisation-name",
            "title": "Organisation Name",
            "components": [
                {
                    "name": "organisation_name",
                    "options": {"hideTitle": False, "classes": ""},
                    "type": "TextField",
                    "title": "What is your organisation's name?",
                    "hint": "This must match the registered legal organisation name",
                    "schema": {},
                }
            ],
            "next": [{"path": "/organisation-alternative-names"}],
        },
        {
            "path": "/organisation-alternative-names",
            "title": "Alternative names of your organisation",
            "components": [
                {"name": "alt_name_1", "options": {}, "type": "TextField", "title": "Alternative name 1", "schema": {}}
            ],
            "next": [{"path": "/organisation-address"}],
        },
        {
            "path": "/organisation-address",
            "title": "Organisation Address",
            "components": [
                {
                    "name": "organisation_address",
                    "options": {},
                    "type": "UkAddressField",
                    "title": "What is your organisation's address?",
                    "schema": {},
                }
            ],
            "next": [{"path": "/organisation-classification"}],
        },
        {
            "path": "/organisation-classification",
            "title": "Organisation Classification",
            "components": [
                {
                    "name": "organisation_classification",
                    "options": {"hideTitle": False, "classes": ""},
                    "type": "RadiosField",
                    "title": "How is your organisation classified?",
                    "list": "classifications_list",
                    "schema": {},
                }
            ],
            "next": [{"path": "/summary"}],
        },
        {
            "path": "/summary",
            "title": "Check your answers",
            "components": [],
            "next": [],
            "controller": "./pages/summary.js",
        },
    ],
    "lists": [
        {
            "name": "classifications_list",
            "type": "string",
            "items": [{"text": "Charity", "value": "charity"}, {"text": "Public Limited Company", "value": "plc"}],
        }
    ],
    "conditions": [],
    "sections": [],
    "outputs": [],
    "skipSummary": False,
    "name": "About your organisation",
}

CONTACT_DETAILS_FORM_JSON = {
    "startPage": "/lead-contact-details",
    "pages": [
        {
            "path": "/lead-contact-details",
            "title": "Lead Contact Details",
            "components": [
                {
                    "name": "lead_contact_name",
                    "options": {},
                    "type": "TextField",
                    "title": "Lead contact full name",
                    "schema": {},
                },
                {
                    "name": "lead_contact_email",
                    "options": {},
                    "type": "EmailAddressField",
                    "title": "Lead contact email address",
                    "schema": {},
                },
                {
                    "name": "lead_contact_phone",
                    "options": {},
                    "type": "TelephoneNumberField",
                    "title": "Lead contact telephone number",
                    "schema": {},
                },
            ],
            "next": [{"path": "/summary"}],
        },
        {
            "path": "/summary",
            "title": "Check your answers",
            "components": [],
            "next": [],
            "controller": "./pages/summary.js",
        },
    ],
    "lists": [],
    "conditions": [],
    "sections": [],
    "outputs": [],
    "skipSummary": False,
    "name": "Contact Details",
}


# NOSONAR Ignore since this data is related to unit tests
def init_salmon_fishing_fund():
    organisation_uuid = uuid4()
    o: Organisation = Organisation(
        organisation_id=organisation_uuid,
        name="Department for Fishing",
        short_name="DF",
        logo_uri="https://www.google.com",
        audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
    )

    f: Fund = Fund(
        fund_id=uuid4(),
        name_json={"en": "Salmon Fishing Fund"},
        title_json={"en": "funding to improve access to salmon fishing"},
        description_json={
            "en": "A £10m fund to improve access to salmon fishing facilities across the devolved nations."
        },
        welsh_available=False,
        short_name=f"SFF{randint(0, 999)}",
        owner_organisation_id=o.organisation_id,
        funding_type=FundingType.COMPETITIVE,
        ggis_scheme_reference_number="G1-SCH-0000092414",
    )

    r: Round = Round(
        round_id=uuid4(),
        fund_id=f.fund_id,
        title_json={"en": "round the first"},
        short_name="TEST",
        **BASIC_ROUND_INFO,
    )
    r2: Round = Round(
        round_id=uuid4(),
        fund_id=f.fund_id,
        title_json={"en": "round the second"},
        short_name="TEST2",
        **BASIC_ROUND_INFO,
    )

    s1: Section = Section(
        section_id=uuid4(), index=1, round_id=r.round_id, name_in_apply_json={"en": "Organisation Information"}
    )
    f1: Form = Form(
        form_id=uuid4(),
        section_id=s1.section_id,
        name_in_apply_json={"en": "About your organisation"},
        section_index=1,
        runner_publish_name="about-your-org",
        form_json=ABOUT_YOUR_ORG_FORM_JSON,
    )
    f2: Form = Form(
        form_id=uuid4(),
        section_id=s1.section_id,
        name_in_apply_json={"en": "Contact Details"},
        section_index=2,
        runner_publish_name="contact-details",
        form_json=CONTACT_DETAILS_FORM_JSON,
    )
    fd: Fund = Fund(
        fund_id=uuid4(),
        name_json={"en": "Cats and Trees Fund"},
        title_json={"en": "funding to rescue more cats from trees"},
        description_json={"en": "A £10m fund to improve access to ladders for rescuing cats stuck up trees."},
        welsh_available=False,
        short_name="CTF",
        owner_organisation_id=o.organisation_id,
        funding_type=FundingType.COMPETITIVE,
        ggis_scheme_reference_number="G2-SCH-0000092414",
    )
    rd: Round = Round(
        round_id=uuid4(),
        fund_id=fd.fund_id,
        title_json={"en": "First Round"},
        short_name="R1",
        **BASIC_ROUND_INFO,
    )
    return {
        "funds": [f, fd],
        "rounds": [r, r2, rd],
        "sections": [s1],
        "forms": [f1, f2],
        "default_next_pages": [
            {"page_id": alt_page_id, "default_next_page_id": page_two_id},
            {"page_id": page_two_id, "default_next_page_id": page_five_id},
        ],
        "organisations": [o],
    }


# NOSONAR Ignore since this data is related to unit tests
def init_unit_test_data() -> dict:
    organisation_uuid = uuid4()
    o: Organisation = Organisation(
        organisation_id=organisation_uuid,
        name=f"Ministry of Testing - {str(organisation_uuid)[:5]}",
        short_name=f"MoT-{str(organisation_uuid)[:5]}",
        logo_uri="https://www.google.com",
        audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
    )
    f: Fund = Fund(
        fund_id=uuid4(),
        name_json={"en": "Unit Test Fund 1"},
        title_json={"en": "funding to improve testing"},
        description_json={"en": "A £10m fund to improve testing across the devolved nations."},
        welsh_available=False,
        short_name=f"UTF{randint(0, 999)}",
        owner_organisation_id=o.organisation_id,
        funding_type=FundingType.COMPETITIVE,
        ggis_scheme_reference_number="G3-SCH-0000092414",
    )
    r: Round = Round(
        round_id=uuid4(),
        fund_id=f.fund_id,
        audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
        title_json={"en": "round the first"},
        short_name=f"UTR{randint(0, 999)}",
        opens=datetime.now(),
        deadline=datetime.now(),
        assessment_start=datetime.now(),
        reminder_date=datetime.now(),
        assessment_deadline=datetime.now(),
        prospectus_link="https://www.google.com",
        privacy_notice_link="https://www.google.com",
        contact_email="test@test.com",
        feedback_link="https://www.google.com",
        project_name_field_id="12312312312",
        guidance_url="https://www.google.com",
        feedback_survey_config={
            "has_feedback_survey": False,
            "has_section_feedback": False,
            "has_research_survey": False,
            "is_feedback_survey_optional": False,
            "is_section_feedback_optional": False,
            "is_research_survey_optional": False,
        },
        eligibility_config={"has_eligibility": False},
        eoi_decision_schema={"en": {"valid": True}, "cy": {"valid": False}},
        status="In progress",
    )
    s1: Section = Section(
        section_id=uuid4(), index=1, round_id=r.round_id, name_in_apply_json={"en": "Organisation Information"}
    )
    f1: Form = Form(
        form_id=uuid4(),
        section_id=s1.section_id,
        name_in_apply_json={"en": "About your organisation"},
        section_index=1,
        runner_publish_name="about-your-org",
        form_json=ABOUT_YOUR_ORG_FORM_JSON,
    )

    return {
        "funds": [f],
        "organisations": [o],
        "rounds": [r],
        "sections": [s1],
        "forms": [f1],
    }


# NOSONAR Ignore since this data is related to unit tests
def fund_without_assessment() -> dict:
    organisation_uuid = uuid4()
    o: Organisation = Organisation(
        organisation_id=organisation_uuid,
        name=f"Ministry of Testing - {str(organisation_uuid)[:5]}",
        short_name=f"MoT-{str(organisation_uuid)[:5]}",
        logo_uri="https://www.google.com",
        audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
    )

    f2: Fund = Fund(
        fund_id=uuid4(),
        name_json={"en": "Unit Test Fund 2"},
        title_json={"en": "funding to improve testing"},
        description_json={"en": "A £10m fund to improve testing across the devolved nations."},
        welsh_available=False,
        short_name=f"UTF{randint(0, 999)}",
        owner_organisation_id=o.organisation_id,
        funding_type=FundingType.COMPETITIVE,
        ggis_scheme_reference_number="G3-SCH-0000092414",
    )

    f2_r1: Round = Round(
        round_id=uuid4(),
        fund_id=f2.fund_id,
        audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
        title_json={"en": "round the first"},
        short_name=f"UTR{randint(0, 999)}",
        opens=datetime.now(),
        deadline=datetime.now(),
        assessment_start=datetime.now(),
        reminder_date=datetime.now(),
        assessment_deadline=datetime.now(),
        prospectus_link="https://www.google.com",
        privacy_notice_link="https://www.google.com",
        contact_email="test@test.com",
        feedback_link="https://www.google.com",
        project_name_field_id="12312312312",
        guidance_url="https://www.google.com",
        feedback_survey_config={
            "has_feedback_survey": False,
            "has_section_feedback": False,
            "has_research_survey": False,
            "is_feedback_survey_optional": False,
            "is_section_feedback_optional": False,
            "is_research_survey_optional": False,
        },
        eligibility_config={"has_eligibility": False},
        eoi_decision_schema={"en": {"valid": True}, "cy": {"valid": False}},
        status="In progress",
    )

    f2_r1_s1: Section = Section(
        section_id=uuid4(), index=1, round_id=f2_r1.round_id, name_in_apply_json={"en": "Organisation Information 2"}
    )

    f2_r1_s2: Section = Section(
        section_id=uuid4(), index=1, round_id=f2_r1.round_id, name_in_apply_json={"en": "Organisation Information 3"}
    )

    f2_r1_s1_f1: Form = Form(
        form_id=uuid4(),
        section_id=f2_r1_s1.section_id,
        name_in_apply_json={"en": "About your organisation"},
        section_index=1,
        runner_publish_name="about-your-org",
        form_json=ABOUT_YOUR_ORG_FORM_JSON,
    )

    f2_r1_s1_f2: Form = Form(
        form_id=uuid4(),
        section_id=f2_r1_s2.section_id,
        name_in_apply_json={"en": "About your organisation 2"},
        section_index=1,
        runner_publish_name="about-your-org",
        form_json=ABOUT_YOUR_ORG_FORM_JSON,
    )
    return {
        "funds": [f2],
        "organisations": [o],
        "rounds": [f2_r1],
        "sections": [f2_r1_s1, f2_r1_s2],
        "forms": [f2_r1_s1_f1, f2_r1_s1_f2],
    }


def insert_test_data(db, test_data=None):
    if test_data is None:
        test_data = {}
    db.session.bulk_save_objects(test_data.get("organisations", []))
    db.session.commit()
    db.session.bulk_save_objects(test_data.get("funds", []))
    db.session.commit()
    db.session.bulk_save_objects(test_data.get("rounds", []))
    db.session.commit()
    db.session.bulk_save_objects(test_data.get("sections", []))
    db.session.commit()
    db.session.bulk_save_objects(test_data.get("forms", []))
    db.session.commit()
