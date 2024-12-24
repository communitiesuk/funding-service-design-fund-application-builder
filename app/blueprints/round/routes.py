import json
from datetime import datetime
from random import randint

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.blueprints.index.routes import all_funds_as_govuk_select_items
from app.blueprints.round.forms import RoundForm, get_datetime
from app.db.models.round import Round
from app.db.queries.clone import clone_single_round
from app.db.queries.fund import get_all_funds
from app.db.queries.round import add_round, get_round_by_id, update_round
from app.shared.helpers import error_formatter

INDEX_BP_DASHBOARD = "index_bp.dashboard"

# Blueprint for routes used by v1 of FAB - using the DB
round_bp = Blueprint(
    "round_bp",
    __name__,
    url_prefix="/round",
    template_folder="templates",
)


@round_bp.route("/<round_id>/clone")
def clone_round(round_id, fund_id):
    cloned = clone_single_round(
        round_id=round_id,
        new_fund_id=fund_id,
        new_short_name=f"R-C{randint(0, 999)}",  # NOSONAR
    )
    flash(f"Cloned new round: {cloned.short_name}")

    return redirect(url_for("fund_bp.view_fund", fund_id=fund_id))


@round_bp.route("", methods=["GET", "POST"])
@round_bp.route("/<round_id>", methods=["GET", "POST"])
def round(round_id=None):
    """
    Renders a template to select a fund and add or update a round to that fund. If saved, validates the round form data
    and saves to DB
    """
    form = RoundForm()
    all_funds = get_all_funds()
    params = {"all_funds": all_funds_as_govuk_select_items(all_funds)}
    params["selected_fund_id"] = request.form.get("fund_id", None)
    params["welsh_availability"] = json.dumps({str(fund.fund_id): fund.welsh_available for fund in all_funds})

    if round_id:
        round = get_round_by_id(round_id)
        form = populate_form_with_round_data(round)

    if form.validate_on_submit():
        if round_id:
            update_existing_round(round, form)
            flash(f"Updated round {round.title_json['en']}")
            return redirect(url_for("fund_bp.view_fund", fund_id=round.fund_id))
        create_new_round(form)
        flash(f"Created round {form.title_en.data}")
        return redirect(url_for(INDEX_BP_DASHBOARD))

    params["round_id"] = round_id
    params["form"] = form

    error = error_formatter(params["form"])
    return render_template("round.html", **params, error=error)


def _convert_json_data_for_form(data) -> str:
    if isinstance(data, dict):
        return json.dumps(data)
    return str(data)


def _convert_form_data_to_json(data) -> dict:
    if data:
        return json.loads(data)
    return {}


def populate_form_with_round_data(round):
    """
    Populate a RoundForm with data from a Round object.

    :param Round round: The round object to populate the form with
    :return: A RoundForm populated with the round data
    """
    round_data = {
        "fund_id": round.fund_id,
        "round_id": round.round_id,
        "title_en": round.title_json.get("en", ""),
        "title_cy": round.title_json.get("cy", ""),
        "short_name": round.short_name,
        "opens": round.opens,
        "deadline": round.deadline,
        "assessment_start": round.assessment_start,
        "reminder_date": round.reminder_date,
        "assessment_deadline": round.assessment_deadline,
        "prospectus_link": round.prospectus_link,
        "privacy_notice_link": round.privacy_notice_link,
        "contact_us_banner_en": round.contact_us_banner_json.get("en", "") if round.contact_us_banner_json else "",
        "contact_us_banner_cy": round.contact_us_banner_json.get("cy", "") if round.contact_us_banner_json else "",
        "reference_contact_page_over_email": "true" if round.reference_contact_page_over_email else "false",
        "contact_email": round.contact_email,
        "contact_phone": round.contact_phone,
        "contact_textphone": round.contact_textphone,
        "support_times": round.support_times,
        "support_days": round.support_days,
        "instructions_en": round.instructions_json.get("en", "") if round.instructions_json else "",
        "instructions_cy": round.instructions_json.get("cy", "") if round.instructions_json else "",
        "feedback_link": round.feedback_link,
        "project_name_field_id": round.project_name_field_id,
        "application_guidance_en": (
            round.application_guidance_json.get("en", "") if round.application_guidance_json else ""
        ),
        "application_guidance_cy": (
            round.application_guidance_json.get("cy", "") if round.application_guidance_json else ""
        ),
        "guidance_url": round.guidance_url,
        "all_uploaded_documents_section_available": (
            "true" if round.all_uploaded_documents_section_available else "false"
        ),
        "application_fields_download_available": "true" if round.application_fields_download_available else "false",
        "display_logo_on_pdf_exports": "true" if round.display_logo_on_pdf_exports else "false",
        "mark_as_complete_enabled": "true" if round.mark_as_complete_enabled else "false",
        "is_expression_of_interest": "true" if round.is_expression_of_interest else "false",
        "has_feedback_survey": (
            "true"
            if round.feedback_survey_config and round.feedback_survey_config.get("has_feedback_survey", "") == "true"
            else "false"
        ),
        "has_section_feedback": (
            "true"
            if round.feedback_survey_config and round.feedback_survey_config.get("has_section_feedback", "") == "true"
            else "false"
        ),
        "has_research_survey": (
            "true"
            if round.feedback_survey_config and round.feedback_survey_config.get("has_research_survey", "") == "true"
            else "false"
        ),
        "is_feedback_survey_optional": (
            "true"
            if round.feedback_survey_config
            and round.feedback_survey_config.get("is_feedback_survey_optional", "") == "true"
            else "false"
        ),
        "is_section_feedback_optional": (
            "true"
            if round.feedback_survey_config
            and round.feedback_survey_config.get("is_section_feedback_optional", "") == "true"
            else "false"
        ),
        "is_research_survey_optional": (
            "true"
            if round.feedback_survey_config
            and round.feedback_survey_config.get("is_research_survey_optional", "") == "true"
            else "false"
        ),
        "eligibility_config": (
            "true"
            if round.eligibility_config and round.eligibility_config.get("has_eligibility", "") == "true"
            else "false"
        ),
        "eoi_decision_schema_en": (
            _convert_json_data_for_form(round.eoi_decision_schema.get("en", "")) if round.eoi_decision_schema else ""
        ),
        "eoi_decision_schema_cy": (
            _convert_json_data_for_form(round.eoi_decision_schema.get("cy", "")) if round.eoi_decision_schema else ""
        ),
    }
    return RoundForm(data=round_data)


def update_existing_round(round, form):
    """
    Update a Round object with the data from a RoundForm.

    :param Round round: The round object to update
    :param RoundForm form: The form with the new round data
    """
    round.title_json = {"en": form.title_en.data or None, "cy": form.title_cy.data or None}
    round.short_name = form.short_name.data
    round.feedback_survey_config = {
        "has_feedback_survey": form.has_feedback_survey.data == "true",
        "has_section_feedback": form.has_section_feedback.data == "true",
        "has_research_survey": form.has_research_survey.data == "true",
        "is_feedback_survey_optional": form.is_feedback_survey_optional.data == "true",
        "is_section_feedback_optional": form.is_section_feedback_optional.data == "true",
        "is_research_survey_optional": form.is_research_survey_optional.data == "true",
    }
    round.opens = get_datetime(form.opens)
    round.deadline = get_datetime(form.deadline)
    round.assessment_start = get_datetime(form.assessment_start)
    round.reminder_date = get_datetime(form.reminder_date)
    round.assessment_deadline = get_datetime(form.assessment_deadline)
    round.prospectus_link = form.prospectus_link.data
    round.privacy_notice_link = form.privacy_notice_link.data
    round.reference_contact_page_over_email = form.reference_contact_page_over_email.data == "true"
    round.contact_email = form.contact_email.data
    round.contact_phone = form.contact_phone.data
    round.contact_textphone = form.contact_textphone.data
    round.support_times = form.support_times.data
    round.support_days = form.support_days.data
    round.feedback_link = form.feedback_link.data
    round.project_name_field_id = form.project_name_field_id.data
    round.guidance_url = form.guidance_url.data
    round.all_uploaded_documents_section_available = form.all_uploaded_documents_section_available.data == "true"
    round.application_fields_download_available = form.application_fields_download_available.data == "true"
    round.display_logo_on_pdf_exports = form.display_logo_on_pdf_exports.data == "true"
    round.mark_as_complete_enabled = form.mark_as_complete_enabled.data == "true"
    round.is_expression_of_interest = form.is_expression_of_interest.data == "true"
    round.short_name = form.short_name.data
    round.contact_us_banner_json = {
        "en": form.contact_us_banner_en.data or None,
        "cy": form.contact_us_banner_cy.data or None,
    }
    round.instructions_json = {"en": form.instructions_en.data or None, "cy": form.instructions_cy.data or None}
    round.application_guidance_json = {
        "en": form.application_guidance_en.data or None,
        "cy": form.application_guidance_cy.data or None,
    }
    round.guidance_url = form.guidance_url.data
    round.all_uploaded_documents_section_available = form.all_uploaded_documents_section_available.data == "true"
    round.application_fields_download_available = form.application_fields_download_available.data == "true"
    round.display_logo_on_pdf_exports = form.display_logo_on_pdf_exports.data == "true"
    round.mark_as_complete_enabled = form.mark_as_complete_enabled.data == "true"
    round.is_expression_of_interest = form.is_expression_of_interest.data == "true"
    round.eligibility_config = {"has_eligibility": form.eligibility_config.data == "true"}
    round.eoi_decision_schema = {
        "en": _convert_form_data_to_json(form.eoi_decision_schema_en.data),
        "cy": _convert_form_data_to_json(form.eoi_decision_schema_cy.data),
    }
    round.audit_info = {"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "update"}
    update_round(round)


def create_new_round(form):
    """
    Create a new Round object with the data from a RoundForm and save it to the database.

    :param RoundForm form: The form with the new round data
    """
    new_round = Round(
        fund_id=form.fund_id.data,
        audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
        title_json={"en": form.title_en.data or None, "cy": form.title_cy.data or None},
        short_name=form.short_name.data,
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
            "en": _convert_form_data_to_json(form.eoi_decision_schema_en.data),
            "cy": _convert_form_data_to_json(form.eoi_decision_schema_cy.data),
        },
    )
    add_round(new_round)
