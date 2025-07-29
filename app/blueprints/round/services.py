import json
from datetime import datetime

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
        "welsh_available": round_obj.fund.welsh_available,
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
        "contact_email": round_obj.contact_email,
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
        "has_feedback_survey": form.has_feedback_survey.data,
        "has_section_feedback": False,  # Not used in form
        "has_research_survey": form.has_research_survey.data,
        "is_feedback_survey_optional": form.is_feedback_survey_optional.data,
        "is_section_feedback_optional": False,  # Not used in form
        "is_research_survey_optional": form.is_research_survey_optional.data,
    }

    # IMPORTANT: convert date sub-form dicts into Python datetime objects
    round_obj.opens = form.opens.data
    round_obj.deadline = form.deadline.data
    round_obj.assessment_start = form.assessment_start.data
    round_obj.reminder_date = form.reminder_date.data
    round_obj.assessment_deadline = form.assessment_deadline.data

    round_obj.prospectus_link = form.prospectus_link.data
    round_obj.privacy_notice_link = form.privacy_notice_link.data
    round_obj.contact_email = form.contact_email.data
    round_obj.feedback_link = form.feedback_link.data
    round_obj.project_name_field_id = form.project_name_field_id.data
    round_obj.guidance_url = form.guidance_url.data
    round_obj.all_uploaded_documents_section_available = False  # Not used in form
    round_obj.application_fields_download_available = form.application_fields_download_available.data
    round_obj.display_logo_on_pdf_exports = form.display_logo_on_pdf_exports.data
    round_obj.mark_as_complete_enabled = form.mark_as_complete_enabled.data
    round_obj.is_expression_of_interest = form.is_expression_of_interest.data
    round_obj.instructions_json = {"en": form.instructions_en.data or None, "cy": form.instructions_cy.data or None}
    round_obj.application_guidance_json = {
        "en": form.application_guidance_en.data or None,
        "cy": form.application_guidance_cy.data or None,
    }
    round_obj.eligibility_config = {"has_eligibility": form.eligibility_config.data}
    round_obj.eoi_decision_schema = {
        "en": convert_form_data_to_json(form.eoi_decision_schema_en.data),
        "cy": convert_form_data_to_json(form.eoi_decision_schema_cy.data)
        if form.eoi_decision_schema_cy.data and form.eoi_decision_schema_cy.data.lower() != "none"
        else None,
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
        opens=form.opens.data,
        deadline=form.deadline.data,
        assessment_start=form.assessment_start.data,
        reminder_date=form.reminder_date.data,
        assessment_deadline=form.assessment_deadline.data,
        prospectus_link=form.prospectus_link.data,
        privacy_notice_link=form.privacy_notice_link.data,
        contact_email=form.contact_email.data,
        instructions_json={"en": form.instructions_en.data or None, "cy": form.instructions_cy.data or None},
        feedback_link=form.feedback_link.data,
        project_name_field_id=form.project_name_field_id.data,
        application_guidance_json={
            "en": form.application_guidance_en.data or None,
            "cy": form.application_guidance_cy.data or None,
        },
        guidance_url=form.guidance_url.data,
        all_uploaded_documents_section_available=False,  # Not used in form
        application_fields_download_available=form.application_fields_download_available.data,
        display_logo_on_pdf_exports=form.display_logo_on_pdf_exports.data,
        mark_as_complete_enabled=form.mark_as_complete_enabled.data,
        is_expression_of_interest=form.is_expression_of_interest.data,
        feedback_survey_config={
            "has_feedback_survey": form.has_feedback_survey.data,
            "has_section_feedback": False,  # Not used in form
            "has_research_survey": form.has_research_survey.data,
            "is_feedback_survey_optional": form.is_feedback_survey_optional.data,
            "is_section_feedback_optional": False,  # Not used in form
            "is_research_survey_optional": form.is_research_survey_optional.data,
        },
        eligibility_config={"has_eligibility": form.eligibility_config.data},
        eoi_decision_schema={
            "en": convert_form_data_to_json(form.eoi_decision_schema_en.data),
            "cy": convert_form_data_to_json(form.eoi_decision_schema_cy.data),
        },
    )
    add_round(new_round)
    return new_round
