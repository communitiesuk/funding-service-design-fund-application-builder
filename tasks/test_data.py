from dataclasses import asdict
from datetime import datetime
from random import randint
from uuid import uuid4

from app.db.models import Component
from app.db.models import ComponentType
from app.db.models import Criteria
from app.db.models import Form
from app.db.models import Fund
from app.db.models import Lizt
from app.db.models import Organisation
from app.db.models import Page
from app.db.models import Round
from app.db.models import Section
from app.db.models import Subcriteria
from app.db.models import Theme
from app.shared.data_classes import Condition
from app.shared.data_classes import ConditionValue

BASIC_FUND_INFO = {
    "name_json": {"en": "Unit Test Fund"},
    "title_json": {"en": "funding to improve testing"},
    "description_json": {"en": "A £10m fund to improve testing across the devolved nations."},
    "welsh_available": False,
    "owner_organisation_id": None,
}
BASIC_ROUND_INFO = {
    "audit_info": {"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
    "opens": "2024-10-01T11:59:00",
    "deadline": "2024-10-31T11:59:00",
    "assessment_start": "2024-10-01T11:59:00",
    "reminder_date": "2024-10-20T11:59:00",
    "assessment_deadline": "2024-11-30T11:59:00",
    "project_name_field_id": 1,
    "prospectus_link": "http://www.google.com",
    "privacy_notice_link": "http://www.google.com",
    "reference_contact_page_over_email": False,
    "contact_email": "help@fab.gov.uk",
    "contact_phone": "01234 123123",
    "contact_textphone": "None",
    "support_times": "12-2",
    "support_days": "Just Mondays",
    "instructions_json": {},
    "feedback_link": None,
    "application_guidance_json": {
        "en": "You can view <a href='{all_questions_url}'>all the questions we will ask you</a> if you want to."
    },
    "guidance_url": None,
    "all_uploaded_documents_section_available": False,
    "application_fields_download_available": False,
    "display_logo_on_pdf_exports": False,
    "mark_as_complete_enabled": False,
    "is_expression_of_interest": False,
    "eoi_decision_schema": {},
    "feedback_survey_config": {
        "has_feedback_survey": False,
        "has_section_feedback": False,
        "is_feedback_survey_optional": False,
        "is_section_feedback_optional": False,
    },
    "eligibility_config": {"has_eligibility": False},
    "contact_us_banner_json": {},
}

page_one_id = uuid4()
page_two_id = uuid4()
page_three_id = uuid4()
page_four_id = uuid4()
page_five_id = uuid4()
alt_page_id = uuid4()


def init_salmon_fishing_fund():
    organisation_uuid = uuid4()
    o: Organisation = Organisation(
        organisation_id=organisation_uuid,
        name="Department for Fishing",
        short_name="DF",
        logo_uri="http://www.google.com",
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
        short_name=f"SFF{randint(0,999)}",
        owner_organisation_id=o.organisation_id,
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
    )
    f2: Form = Form(
        form_id=uuid4(),
        section_id=s1.section_id,
        name_in_apply_json={"en": "Contact Details"},
        section_index=2,
        runner_publish_name="contact-details",
    )
    p1: Page = Page(
        page_id=page_one_id,
        form_id=f1.form_id,
        display_path="organisation-name",
        name_in_apply_json={"en": "Organisation Name"},
        form_index=1,
    )
    p2: Page = Page(
        page_id=page_two_id,
        display_path="organisation-address",
        form_id=f1.form_id,
        name_in_apply_json={"en": "Organisation Address"},
        form_index=3,
    )
    p3: Page = Page(
        page_id=page_three_id,
        form_id=f2.form_id,
        display_path="lead-contact-details",
        name_in_apply_json={"en": "Lead Contact Details"},
        form_index=1,
    )
    p5: Page = Page(
        page_id=page_five_id,
        display_path="organisation-classification",
        form_id=f1.form_id,
        name_in_apply_json={"en": "Organisation Classification"},
        form_index=4,
        default_next_page_id=None,
    )
    p_org_alt_names: Page = Page(
        page_id=alt_page_id,
        form_id=f1.form_id,
        display_path="organisation-alternative-names",
        name_in_apply_json={"en": "Alternative names of your organisation"},
        form_index=2,
        is_template=True,
    )
    cri1: Criteria = Criteria(criteria_id=uuid4(), index=1, round_id=r.round_id, name="Unscored", weighting=0.0)
    sc1: Subcriteria = Subcriteria(
        subcriteria_id=uuid4(), criteria_index=1, criteria_id=cri1.criteria_id, name="Organisation Information"
    )
    t1: Theme = Theme(
        theme_id=uuid4(), subcriteria_id=sc1.subcriteria_id, name="General Information", subcriteria_index=1
    )
    t2: Theme = Theme(theme_id=uuid4(), subcriteria_id=sc1.subcriteria_id, name="Contact Details", subcriteria_index=1)
    c4: Component = Component(
        component_id=uuid4(),
        page_id=p3.page_id,
        title="Main Contact Name",
        type=ComponentType.TEXT_FIELD,
        page_index=1,
        theme_id=t2.theme_id,
        theme_index=1,
        options={"hideTitle": False, "classes": ""},
        runner_component_name="main_contact_name",
    )
    c5: Component = Component(
        component_id=uuid4(),
        page_id=p3.page_id,
        title="Main Contact Email",
        type=ComponentType.EMAIL_ADDRESS_FIELD,
        page_index=2,
        theme_id=t2.theme_id,
        theme_index=4,
        options={"hideTitle": False, "classes": ""},
        runner_component_name="main_contact_email",
    )
    c6: Component = Component(
        component_id=uuid4(),
        page_id=p3.page_id,
        title="Main Contact Address",
        type=ComponentType.UK_ADDRESS_FIELD,
        page_index=3,
        theme_id=t2.theme_id,
        theme_index=3,
        options={"hideTitle": False, "classes": ""},
        runner_component_name="main_contact_address",
    )
    c1: Component = Component(
        component_id=uuid4(),
        page_id=p1.page_id,
        title="What is your organisation's name?",
        hint_text="This must match the registered legal organisation name",
        type=ComponentType.TEXT_FIELD,
        page_index=1,
        theme_id=t1.theme_id,
        theme_index=1,
        options={"hideTitle": False, "classes": ""},
        runner_component_name="organisation_name",
    )
    c3: Component = Component(
        component_id=uuid4(),
        page_id=p1.page_id,
        title="Does your organisation use any other names?",
        type=ComponentType.YES_NO_FIELD,
        page_index=2,
        theme_id=t1.theme_id,
        theme_index=2,
        options={"hideTitle": False, "classes": ""},
        runner_component_name="does_your_organisation_use_other_names",
        conditions=[
            asdict(
                Condition(
                    name="organisation_other_names_no",
                    display_name="Other Name No",
                    destination_page_path="/organisation-address",
                    value=ConditionValue(
                        name="Other Name No",
                        conditions=[
                            {
                                "field": {
                                    "name": "does_your_organisation_use_other_names",
                                    "type": "YesNoField",
                                    "display": "Does your organisation use other names?",
                                },
                                "operator": "is",
                                "value": {"type": "Value", "value": "false", "display": "false"},
                            }
                        ],
                    ),
                )
            ),
            asdict(
                Condition(
                    name="organisation_other_names_yes",
                    display_name="Other Name Yes",
                    destination_page_path="/organisation-alternative-names",
                    value=ConditionValue(
                        name="Other Name Yes",
                        conditions=[
                            {
                                "field": {
                                    "name": "does_your_organisation_use_other_names",
                                    "type": "YesNoField",
                                    "display": "Does your organisation use other names?",
                                },
                                "operator": "is",
                                "value": {"type": "Value", "value": "true", "display": "true"},
                            }
                        ],
                    ),
                )
            ),
        ],
    )
    c2: Component = Component(
        component_id=uuid4(),
        page_id=p2.page_id,
        title="What is your organisation's address?",
        hint_text="This must match the registered organisation address",
        type=ComponentType.UK_ADDRESS_FIELD,
        page_index=1,
        theme_id=t1.theme_id,
        theme_index=5,
        options={"hideTitle": False, "classes": ""},
        runner_component_name="organisation_address",
    )
    c7: Component = Component(
        component_id=uuid4(),
        page_id=p_org_alt_names.page_id,
        title="Alternative Name 1",
        type=ComponentType.TEXT_FIELD,
        page_index=1,
        theme_id=None,
        theme_index=None,
        options={"hideTitle": False, "classes": ""},
        runner_component_name="alt_name_1",
    )
    l1: Lizt = Lizt(
        list_id=uuid4(),
        name="classifications_list",
        type="string",
        items=[{"text": "Charity", "value": "charity"}, {"text": "Public Limited Company", "value": "plc"}],
        is_template=True,
    )
    c8: Component = Component(
        component_id=uuid4(),
        page_id=p5.page_id,
        title="How is your organisation classified?",
        type=ComponentType.RADIOS_FIELD,
        page_index=1,
        theme_id=t1.theme_id,
        theme_index=6,
        options={"hideTitle": False, "classes": ""},
        runner_component_name="organisation_classification",
        list_id=l1.list_id,
    )

    fd: Fund = Fund(
        fund_id=uuid4(),
        name_json={"en": "Cats and Trees Fund"},
        title_json={"en": "funding to rescue more cats from trees"},
        description_json={"en": "A £10m fund to improve access to ladders for rescuing cats stuck up trees."},
        welsh_available=False,
        short_name="CTF",
        owner_organisation_id=o.organisation_id,
    )

    rd: Round = Round(
        round_id=uuid4(),
        fund_id=fd.fund_id,
        title_json={"en": "First Round"},
        short_name="R1",
        **BASIC_ROUND_INFO,
    )
    return {
        "lists": [l1],
        "funds": [f, fd],
        "rounds": [r, r2, rd],
        "sections": [s1],
        "forms": [f1, f2],
        "pages": [p1, p2, p3, p5, p_org_alt_names],
        "default_next_pages": [
            {"page_id": alt_page_id, "default_next_page_id": page_two_id},
            {"page_id": page_two_id, "default_next_page_id": page_five_id},
        ],
        "components": [c1, c2, c4, c5, c6, c8, c3, c7],
        "criteria": [cri1],
        "subcriteria": [sc1],
        "themes": [t1, t2],
        "organisations": [o],
    }


def init_unit_test_data() -> dict:
    organisation_uuid = uuid4()
    o: Organisation = Organisation(
        organisation_id=organisation_uuid,
        name=f"Ministry of Testing - {str(organisation_uuid)[:5]}",
        short_name=f"MoT-{str(organisation_uuid)[:5]}",
        logo_uri="http://www.google.com",
        audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
    )

    f: Fund = Fund(
        fund_id=uuid4(),
        name_json={"en": "Unit Test Fund 1"},
        title_json={"en": "funding to improve testing"},
        description_json={"en": "A £10m fund to improve testing across the devolved nations."},
        welsh_available=False,
        short_name=f"UTF{randint(0,999)}",
        owner_organisation_id=o.organisation_id,
    )

    r: Round = Round(
        round_id=uuid4(),
        fund_id=f.fund_id,
        audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
        title_json={"en": "round the first"},
        short_name=f"UTR{randint(0,999)}",
        opens=datetime.now(),
        deadline=datetime.now(),
        assessment_start=datetime.now(),
        reminder_date=datetime.now(),
        assessment_deadline=datetime.now(),
        prospectus_link="http://www.google.com",
        privacy_notice_link="http://www.google.com",
    )
    # r2: Round = Round(
    #     round_id=uuid4(),
    #     fund_id=f.fund_id,
    #     audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
    #     title_json={"en": "round the second"},
    #     short_name=f"UTR{randint(0,999)}",
    #     opens=datetime.now(),
    #     deadline=datetime.now(),
    #     assessment_start=datetime.now(),
    #     reminder_date=datetime.now(),
    #     assessment_deadline=datetime.now(),
    #     prospectus_link="http://www.google.com",
    #     privacy_notice_link="http://www.google.com",
    # )

    s1: Section = Section(
        section_id=uuid4(), index=1, round_id=r.round_id, name_in_apply_json={"en": "Organisation Information"}
    )
    f1: Form = Form(
        form_id=uuid4(),
        section_id=s1.section_id,
        name_in_apply_json={"en": "About your organisation"},
        section_index=1,
        runner_publish_name="about-your-org",
    )
    p1: Page = Page(
        page_id=uuid4(),
        form_id=f1.form_id,
        display_path="organisation-name",
        name_in_apply_json={"en": "Organisation Name"},
        form_index=1,
        default_next_page_id=None,
    )

    cri1: Criteria = Criteria(criteria_id=uuid4(), index=1, round_id=r.round_id, name="Unscored", weighting=0.0)
    sc1: Subcriteria = Subcriteria(
        subcriteria_id=uuid4(), criteria_index=1, criteria_id=cri1.criteria_id, name="Organisation Information"
    )
    t1: Theme = Theme(
        theme_id=uuid4(), subcriteria_id=sc1.subcriteria_id, name="General Information", subcriteria_index=1
    )

    c1: Component = Component(
        component_id=uuid4(),
        page_id=p1.page_id,
        title="What is your organisation's name?",
        hint_text="This must match the registered legal organisation name",
        type=ComponentType.TEXT_FIELD,
        page_index=1,
        theme_id=t1.theme_id,
        theme_index=1,
        options={"hideTitle": False, "classes": ""},
        runner_component_name="organisation_name",
    )

    l1: Lizt = Lizt(
        list_id=uuid4(),
        name="classifications_list",
        type="string",
        items=[{"text": "Charity", "value": "charity"}, {"text": "Public Limited Company", "value": "plc"}],
        is_template=True,
    )
    c_with_list: Component = Component(
        component_id=uuid4(),
        page_id=p1.page_id,
        title="How is your organisation classified?",
        type=ComponentType.RADIOS_FIELD,
        page_index=2,
        theme_id=t1.theme_id,
        theme_index=6,
        options={"hideTitle": False, "classes": ""},
        runner_component_name="organisation_classification",
        list_id=l1.list_id,
    )
    return {
        "lists": [l1],
        "funds": [f],
        "organisations": [o],
        "rounds": [r],
        "sections": [s1],
        "forms": [f1],
        "pages": [p1],
        "components": [c1, c_with_list],
        "criteria": [cri1],
        "subcriteria": [sc1],
        "themes": [t1],
    }


def add_default_page_paths(db, default_next_page_config):
    # set up the default paths
    for page_config in default_next_page_config:
        page = Page.query.filter_by(page_id=page_config["page_id"]).first()
        page.default_next_page_id = page_config["default_next_page_id"]
    db.session.commit()


def insert_test_data(db, test_data={}):
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
    db.session.bulk_save_objects(test_data.get("pages", []))
    db.session.commit()
    add_default_page_paths(db, test_data.get("default_next_pages", []))
    db.session.bulk_save_objects(test_data.get("criteria", []))
    db.session.commit()
    db.session.bulk_save_objects(test_data.get("subcriteria", []))
    db.session.commit()
    db.session.bulk_save_objects(test_data.get("themes", []))
    db.session.commit()
    db.session.bulk_save_objects(test_data.get("lists", []))
    db.session.commit()
    db.session.bulk_save_objects(test_data.get("components", []))
    db.session.commit()
