import json
from datetime import datetime

from app.blueprints.round.forms import get_datetime
from app.db.models.round import Round
from app.db.queries.round import add_round, update_round


def convert_json_data_for_form(data) -> str:
    if isinstance(data, dict):
        return json.dumps(data)
    return str(data)


def convert_form_data_to_json(data) -> dict:
    if data:
        return json.loads(data)
    return {}


def populate_form_with_round_data(round_obj, form_class):
    round_data = {
        "fund_id": round_obj.fund_id,
        "round_id": round_obj.round_id,
        "title_en": round_obj.title_json.get("en", ""),
        "title_cy": round_obj.title_json.get("cy", ""),
        "short_name": round_obj.short_name,
        "opens": round_obj.opens,
        "deadline": round_obj.deadline,
        "assessment_start": round_obj.assessment_start,
        "reminder_date": round_obj.reminder_date,
        "assessment_deadline": round_obj.assessment_deadline,
        "prospectus_link": round_obj.prospectus_link,
        "privacy_notice_link": round_obj.privacy_notice_link,
        "contact_us_banner_en": round_obj.contact_us_banner_json.get("en", "")
        if round_obj.contact_us_banner_json
        else "",
        "contact_us_banner_cy": round_obj.contact_us_banner_json.get("cy", "")
        if round_obj.contact_us_banner_json
        else "",
        "reference_contact_page_over_email": "true" if round_obj.reference_contact_page_over_email else "false",
        "contact_email": round_obj.contact_email,
        "contact_phone": round_obj.contact_phone,
        "contact_textphone": round_obj.contact_textphone,
        "support_times": round_obj.support_times,
        "support_days": round_obj.support_days,
        "instructions_en": round_obj.instructions_json.get("en", "") if round_obj.instructions_json else "",
        "instructions_cy": round_obj.instructions_json.get("cy", "") if round_obj.instructions_json else "",
        "feedback_link": round_obj.feedback_link,
        "project_name_field_id": round_obj.project_name_field_id,
        "application_guidance_en": (
            round_obj.application_guidance_json.get("en", "") if round_obj.application_guidance_json else ""
        ),
        "application_guidance_cy": (
            round_obj.application_guidance_json.get("cy", "") if round_obj.application_guidance_json else ""
        ),
        "guidance_url": round_obj.guidance_url,
        "all_uploaded_documents_section_available": (
            "true" if round_obj.all_uploaded_documents_section_available else "false"
        ),
        "application_fields_download_available": (
            "true" if round_obj.application_fields_download_available else "false"
        ),
        "display_logo_on_pdf_exports": "true" if round_obj.display_logo_on_pdf_exports else "false",
        "mark_as_complete_enabled": "true" if round_obj.mark_as_complete_enabled else "false",
        "is_expression_of_interest": "true" if round_obj.is_expression_of_interest else "false",
        "has_feedback_survey": (
            "true"
            if round_obj.feedback_survey_config and round_obj.feedback_survey_config.get("has_feedback_survey")
            else "false"
        ),
        "has_section_feedback": (
            "true"
            if round_obj.feedback_survey_config and round_obj.feedback_survey_config.get("has_section_feedback")
            else "false"
        ),
        "has_research_survey": (
            "true"
            if round_obj.feedback_survey_config and round_obj.feedback_survey_config.get("has_research_survey")
            else "false"
        ),
        "is_feedback_survey_optional": (
            "true"
            if round_obj.feedback_survey_config and round_obj.feedback_survey_config.get("is_feedback_survey_optional")
            else "false"
        ),
        "is_section_feedback_optional": (
            "true"
            if round_obj.feedback_survey_config and round_obj.feedback_survey_config.get("is_section_feedback_optional")
            else "false"
        ),
        "is_research_survey_optional": (
            "true"
            if round_obj.feedback_survey_config and round_obj.feedback_survey_config.get("is_research_survey_optional")
            else "false"
        ),
        "eligibility_config": (
            "true"
            if round_obj.eligibility_config and round_obj.eligibility_config.get("has_eligibility") == "true"
            else "false"
        ),
        "eoi_decision_schema_en": (
            convert_json_data_for_form(round_obj.eoi_decision_schema.get("en", ""))
            if round_obj.eoi_decision_schema
            else ""
        ),
        "eoi_decision_schema_cy": (
            convert_json_data_for_form(round_obj.eoi_decision_schema.get("cy", ""))
            if round_obj.eoi_decision_schema
            else ""
        ),
    }
    return form_class(data=round_data)


def update_existing_round(round_obj, form, user="dummy_user"):
    round_obj.title_json = {"en": form.title_en.data or None, "cy": form.title_cy.data or None}
    round_obj.short_name = form.short_name.data
    round_obj.feedback_survey_config = {
        "has_feedback_survey": form.has_feedback_survey.data == "true",
        "has_section_feedback": form.has_section_feedback.data == "true",
        "has_research_survey": form.has_research_survey.data == "true",
        "is_feedback_survey_optional": form.is_feedback_survey_optional.data == "true",
        "is_section_feedback_optional": form.is_section_feedback_optional.data == "true",
        "is_research_survey_optional": form.is_research_survey_optional.data == "true",
    }

    # IMPORTANT: convert date sub-form dicts into Python datetime objects
    round_obj.opens = get_datetime(form.opens)
    round_obj.deadline = get_datetime(form.deadline)
    round_obj.assessment_start = get_datetime(form.assessment_start)
    round_obj.reminder_date = get_datetime(form.reminder_date)
    round_obj.assessment_deadline = get_datetime(form.assessment_deadline)

    round_obj.prospectus_link = form.prospectus_link.data
    round_obj.privacy_notice_link = form.privacy_notice_link.data
    round_obj.reference_contact_page_over_email = form.reference_contact_page_over_email.data == "true"
    round_obj.contact_email = form.contact_email.data
    round_obj.contact_phone = form.contact_phone.data
    round_obj.contact_textphone = form.contact_textphone.data
    round_obj.support_times = form.support_times.data
    round_obj.support_days = form.support_days.data
    round_obj.feedback_link = form.feedback_link.data
    round_obj.project_name_field_id = form.project_name_field_id.data
    round_obj.guidance_url = form.guidance_url.data
    round_obj.all_uploaded_documents_section_available = form.all_uploaded_documents_section_available.data == "true"
    round_obj.application_fields_download_available = form.application_fields_download_available.data == "true"
    round_obj.display_logo_on_pdf_exports = form.display_logo_on_pdf_exports.data == "true"
    round_obj.mark_as_complete_enabled = form.mark_as_complete_enabled.data == "true"
    round_obj.is_expression_of_interest = form.is_expression_of_interest.data == "true"
    round_obj.contact_us_banner_json = {
        "en": form.contact_us_banner_en.data or None,
        "cy": form.contact_us_banner_cy.data or None,
    }
    round_obj.instructions_json = {"en": form.instructions_en.data or None, "cy": form.instructions_cy.data or None}
    round_obj.application_guidance_json = {
        "en": form.application_guidance_en.data or None,
        "cy": form.application_guidance_cy.data or None,
    }
    round_obj.eligibility_config = {"has_eligibility": form.eligibility_config.data == "true"}
    round_obj.eoi_decision_schema = {
        "en": convert_form_data_to_json(form.eoi_decision_schema_en.data),
        "cy": convert_form_data_to_json(form.eoi_decision_schema_cy.data),
    }
    round_obj.audit_info = {"user": user, "timestamp": datetime.now().isoformat(), "action": "update"}
    update_round(round_obj)


def create_new_round(form, user="dummy_user"):
    new_round = Round(
        fund_id=form.fund_id.data,
        audit_info={"user": user, "timestamp": datetime.now().isoformat(), "action": "create"},
        title_json={"en": form.title_en.data or None, "cy": form.title_cy.data or None},
        short_name=form.short_name.data,
        # Again convert each date dict to a datetime object
        opens=get_datetime(form.opens),
        deadline=get_datetime(form.deadline),
        assessment_start=get_datetime(form.assessment_start),
        reminder_date=get_datetime(form.reminder_date),
        assessment_deadline=get_datetime(form.assessment_deadline),
        prospectus_link=form.prospectus_link.data,
        privacy_notice_link=form.privacy_notice_link.data,
        contact_us_banner_json={
            "en": form.contact_us_banner_en.data or None,
            "cy": form.contact_us_banner_cy.data or None,
        },
        reference_contact_page_over_email=form.reference_contact_page_over_email.data == "true",
        contact_email=form.contact_email.data,
        contact_phone=form.contact_phone.data,
        contact_textphone=form.contact_textphone.data,
        support_times=form.support_times.data,
        support_days=form.support_days.data,
        instructions_json={"en": form.instructions_en.data or None, "cy": form.instructions_cy.data or None},
        feedback_link=form.feedback_link.data,
        project_name_field_id=form.project_name_field_id.data,
        application_guidance_json={
            "en": form.application_guidance_en.data or None,
            "cy": form.application_guidance_cy.data or None,
        },
        guidance_url=form.guidance_url.data,
        all_uploaded_documents_section_available=form.all_uploaded_documents_section_available.data == "true",
        application_fields_download_available=form.application_fields_download_available.data == "true",
        display_logo_on_pdf_exports=form.display_logo_on_pdf_exports.data == "true",
        mark_as_complete_enabled=form.mark_as_complete_enabled.data == "true",
        is_expression_of_interest=form.is_expression_of_interest.data == "true",
        feedback_survey_config={
            "has_feedback_survey": form.has_feedback_survey.data == "true",
            "has_section_feedback": form.has_section_feedback.data == "true",
            "has_research_survey": form.has_research_survey.data == "true",
            "is_feedback_survey_optional": form.is_feedback_survey_optional.data == "true",
            "is_section_feedback_optional": form.is_section_feedback_optional.data == "true",
            "is_research_survey_optional": form.is_research_survey_optional.data == "true",
        },
        eligibility_config={"has_eligibility": form.eligibility_config.data == "true"},
        eoi_decision_schema={
            "en": convert_form_data_to_json(form.eoi_decision_schema_en.data),
            "cy": convert_form_data_to_json(form.eoi_decision_schema_cy.data),
        },
    )
    add_round(new_round)
    return new_round
