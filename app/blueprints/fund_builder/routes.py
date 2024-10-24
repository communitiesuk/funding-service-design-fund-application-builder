import json
import os
import shutil
from datetime import datetime
from random import randint

import requests
from flask import Blueprint
from flask import Response
from flask import after_this_request
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_file
from flask import url_for

from app.all_questions.metadata_utils import generate_print_data_for_sections
from app.blueprints.fund_builder.forms.fund import FundForm
from app.blueprints.fund_builder.forms.round import RoundForm
from app.blueprints.fund_builder.forms.round import get_datetime
from app.blueprints.fund_builder.forms.section import SectionForm
from app.db.models.fund import Fund
from app.db.models.fund import FundingType
from app.db.models.round import Round
from app.db.queries.application import clone_single_form
from app.db.queries.application import clone_single_round
from app.db.queries.application import delete_form_from_section
from app.db.queries.application import delete_section_from_round
from app.db.queries.application import get_all_template_forms
from app.db.queries.application import get_form_by_id
from app.db.queries.application import get_section_by_id
from app.db.queries.application import insert_new_section
from app.db.queries.application import move_form_down
from app.db.queries.application import move_form_up
from app.db.queries.application import move_section_down
from app.db.queries.application import move_section_up
from app.db.queries.application import update_section
from app.db.queries.fund import add_fund
from app.db.queries.fund import get_all_funds
from app.db.queries.fund import get_fund_by_id
from app.db.queries.fund import update_fund
from app.db.queries.round import add_round
from app.db.queries.round import get_round_by_id
from app.db.queries.round import update_round
from app.export_config.generate_all_questions import print_html
from app.export_config.generate_form import build_form_json
from app.export_config.generate_fund_round_config import generate_config_for_round
from app.export_config.generate_fund_round_form_jsons import (
    generate_form_jsons_for_round,
)
from app.export_config.generate_fund_round_html import generate_all_round_html
from config import Config

BUILD_FUND_BP_INDEX = "build_fund_bp.index"

# Blueprint for routes used by v1 of FAB - using the DB
build_fund_bp = Blueprint(
    "build_fund_bp",
    __name__,
    url_prefix="/",
    template_folder="templates",
)


@build_fund_bp.route("/")
def index():
    return render_template("index.html")


@build_fund_bp.route("/fund/round/<round_id>/section", methods=["GET", "POST"])
def section(round_id):
    round_obj = get_round_by_id(round_id)
    fund_obj = get_fund_by_id(round_obj.fund_id)
    form: SectionForm = SectionForm()
    form.round_id.data = round_id
    params = {
        "round_id": str(round_id),
    }
    existing_section = None
    # TODO there must be a better way than a pile of ifs...
    if request.args.get("action") == "remove":
        delete_section_from_round(round_id=round_id, section_id=request.args.get("section_id"), cascade=True)
        return redirect(url_for("build_fund_bp.build_application", round_id=round_id))
    if request.args.get("action") == "move_up":
        move_section_up(round_id=round_id, section_index_to_move_up=int(request.args.get("index")))
        return redirect(url_for("build_fund_bp.build_application", round_id=round_id))
    if request.args.get("action") == "move_down":
        move_section_down(round_id=round_id, section_index_to_move_down=int(request.args.get("index")))
        return redirect(url_for("build_fund_bp.build_application", round_id=round_id))
    if form.validate_on_submit():
        count_existing_sections = len(round_obj.sections)
        if form.section_id.data:
            update_section(
                form.section_id.data,
                {
                    "name_in_apply_json": {"en": form.name_in_apply_en.data},
                },
            )
        else:
            insert_new_section(
                {
                    "round_id": form.round_id.data,
                    "name_in_apply_json": {"en": form.name_in_apply_en.data},
                    "index": max(count_existing_sections + 1, 1),
                }
            )

        # flash(f"Saved section {form.name_in_apply_en.data}")
        return redirect(url_for("build_fund_bp.build_application", round_id=round_obj.round_id))
    if section_id := request.args.get("section_id"):
        existing_section = get_section_by_id(section_id)
        form.section_id.data = section_id
        form.name_in_apply_en.data = existing_section.name_in_apply_json["en"]
        params["forms_in_section"] = existing_section.forms
        params["available_template_forms"] = [
            {"text": f"{f.template_name} - {f.name_in_apply_json['en']}", "value": str(f.form_id)}
            for f in get_all_template_forms()
        ]

    params["breadcrumb_items"] = [
        {"text": "Home", "href": url_for(BUILD_FUND_BP_INDEX)},
        {"text": fund_obj.name_json["en"], "href": url_for("build_fund_bp.view_fund", fund_id=fund_obj.fund_id)},
        {
            "text": round_obj.title_json["en"],
            "href": url_for("build_fund_bp.build_application", fund_id=fund_obj.fund_id, round_id=round_obj.round_id),
        },
        {"text": existing_section.name_in_apply_json["en"] if existing_section else "Add Section", "href": "#"},
    ]
    return render_template("section.html", form=form, **params)


@build_fund_bp.route("/fund/round/<round_id>/section/<section_id>/forms", methods=["POST", "GET"])
def configure_forms_in_section(round_id, section_id):
    if request.method == "GET":
        if request.args.get("action") == "remove":
            form_id = request.args.get("form_id")
            delete_form_from_section(section_id=section_id, form_id=form_id, cascade=True)
        if request.args.get("action") == "move_up":
            move_form_up(section_id=section_id, form_index_to_move_up=int(request.args.get("index")))
        if request.args.get("action") == "move_down":
            move_form_down(section_id=section_id, form_index_to_move_down=int(request.args.get("index")))

    if request.method == "POST":
        template_id = request.form.get("template_id")
        section = get_section_by_id(section_id=section_id)
        new_section_index = max(len(section.forms) + 1, 1)
        clone_single_form(form_id=template_id, new_section_id=section_id, section_index=new_section_index)

    return redirect(url_for("build_fund_bp.section", round_id=round_id, section_id=section_id))


def all_funds_as_govuk_select_items(all_funds: list) -> list:
    """
    Reformats a list of funds into a list of display/value items that can be passed to a govUk select macro
    in the html
    """
    return [{"text": f"{f.short_name} - {f.name_json['en']}", "value": str(f.fund_id)} for f in all_funds]


@build_fund_bp.route("/fund/view", methods=["GET", "POST"])
def view_fund():
    """
    Renders a template providing a drop down list of funds. If a fund is selected, renders its config info
    """
    params = {"all_funds": all_funds_as_govuk_select_items(get_all_funds())}
    fund = None
    if request.method == "POST":
        fund_id = request.form.get("fund_id")
    else:
        fund_id = request.args.get("fund_id")
    if fund_id:
        fund = get_fund_by_id(fund_id)
        params["fund"] = fund
        params["selected_fund_id"] = fund_id
    params["breadcrumb_items"] = [
        {"text": "Home", "href": url_for(BUILD_FUND_BP_INDEX)},
        {"text": fund.title_json["en"] if fund else "Manage Application Configuration", "href": "#"},
    ]

    return render_template("fund_config.html", **params)


@build_fund_bp.route("/fund/round/<round_id>/application_config")
def build_application(round_id):
    """
    Renders a template displaying application configuration info for the chosen round
    """
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    breadcrumb_items = [
        {"text": "Home", "href": url_for(BUILD_FUND_BP_INDEX)},
        {"text": fund.name_json["en"], "href": url_for("build_fund_bp.view_fund", fund_id=fund.fund_id)},
        {"text": round.title_json["en"], "href": "#"},
    ]
    return render_template("build_application.html", round=round, fund=fund, breadcrumb_items=breadcrumb_items)


@build_fund_bp.route("/fund/<fund_id>/round/<round_id>/clone")
def clone_round(round_id, fund_id):

    cloned = clone_single_round(
        round_id=round_id, new_fund_id=fund_id, new_short_name=f"R-C{randint(0,999)}"  # nosec B311
    )
    flash(f"Cloned new round: {cloned.short_name}")

    return redirect(url_for("build_fund_bp.view_fund", fund_id=fund_id))


@build_fund_bp.route("/fund", methods=["GET", "POST"])
@build_fund_bp.route("/fund/<fund_id>", methods=["GET", "POST"])
def fund(fund_id=None):
    """
    Renders a template to allow a user to add or update a fund, when saved validates the form data and saves to DB
    """
    if fund_id:
        fund = get_fund_by_id(fund_id)
        fund_data = {
            "fund_id": fund.fund_id,
            "name_en": fund.name_json.get("en", ""),
            "name_cy": fund.name_json.get("cy", ""),
            "title_en": fund.title_json.get("en", ""),
            "title_cy": fund.title_json.get("cy", ""),
            "short_name": fund.short_name,
            "description_en": fund.description_json.get("en", ""),
            "description_cy": fund.description_json.get("cy", ""),
            "welsh_available": "true" if fund.welsh_available else "false",
            "funding_type": fund.funding_type.value,
        }
        form = FundForm(data=fund_data)
    else:
        form = FundForm()

    if form.validate_on_submit():
        if fund_id:
            fund.name_json["en"] = form.name_en.data
            fund.name_json["cy"] = form.name_cy.data
            fund.title_json["en"] = form.title_en.data
            fund.title_json["cy"] = form.title_cy.data
            fund.description_json["en"] = form.description_en.data
            fund.description_json["cy"] = form.description_cy.data
            fund.welsh_available = form.welsh_available.data == "true"
            fund.short_name = form.short_name.data
            fund.audit_info = {"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "update"}
            fund.funding_type = form.funding_type.data
            update_fund(fund)
            flash(f"Updated fund {form.title_en.data}")
            return redirect(url_for("build_fund_bp.view_fund", fund_id=fund.fund_id))
        else:
            new_fund = Fund(
                name_json={"en": form.name_en.data},
                title_json={"en": form.title_en.data},
                description_json={"en": form.description_en.data},
                welsh_available=form.welsh_available.data == "true",
                short_name=form.short_name.data,
                audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
                funding_type=FundingType(form.funding_type.data),
            )
            add_fund(new_fund)
            flash(f"Created fund {form.name_en.data}")
        return redirect(url_for(BUILD_FUND_BP_INDEX))

    return render_template("fund.html", form=form, fund_id=fund_id)


@build_fund_bp.route("/round", methods=["GET", "POST"])
@build_fund_bp.route("/round/<round_id>", methods=["GET", "POST"])
def round(round_id=None):
    """
    Renders a template to select a fund and add or update a round to that fund. If saved, validates the round form data
    and saves to DB
    """
    all_funds = get_all_funds()
    form = RoundForm()

    if round_id:
        round = get_round_by_id(round_id)
        form = populate_form_with_round_data(round)

    if form.validate_on_submit():
        if round_id:
            update_existing_round(round, form)
            flash(f"Updated round {round.title_json['en']}")
            return redirect(url_for("build_fund_bp.view_fund", fund_id=round.fund_id))
        else:
            create_new_round(form)
            flash(f"Created round {form.title_en.data}")
        return redirect(url_for(BUILD_FUND_BP_INDEX))

    return render_template(
        "round.html",
        form=form,
        all_funds=all_funds_as_govuk_select_items(all_funds),
        round_id=round_id,
    )


def populate_form_with_round_data(round):
    """
    Populate a RoundForm with data from a Round object.

    :param Round round: The round object to populate the form with
    :return: A RoundForm populated with the round data
    """
    round_data = {
        "fund_id": round.fund_id,
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
        "feedback_survey_config": round.feedback_survey_config,
        "eligibility_config": (
            "true"
            if round.eligibility_config and round.eligibility_config.get("has_eligibility", "") == "true"
            else "false"
        ),
        "eoi_decision_schema_en": round.eoi_decision_schema.get("en", "") if round.eoi_decision_schema else "",
        "eoi_decision_schema_cy": round.eoi_decision_schema.get("cy", "") if round.eoi_decision_schema else "",
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
    round.feedback_survey_config = form.feedback_survey_config.data
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
    round.eligibility_config = {"has_eligibility": form.eligibility_config.data}
    round.eoi_decision_schema = {"en": form.eoi_decision_schema_en.data or None, "cy": form.eoi_decision_schema_cy.data or None}
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
        title_json={"en": form.title_en.data or None, "cy":form.title_cy.data or None},
        short_name=form.short_name.data,
        opens=get_datetime(form.opens),
        deadline=get_datetime(form.deadline),
        assessment_start=get_datetime(form.assessment_start),
        reminder_date=get_datetime(form.reminder_date),
        assessment_deadline=get_datetime(form.assessment_deadline),
        prospectus_link=form.prospectus_link.data,
        privacy_notice_link=form.privacy_notice_link.data,
        contact_us_banner_json={"en": form.contact_us_banner_en.data or None, "cy": form.contact_us_banner_cy.data or None},
        reference_contact_page_over_email=form.reference_contact_page_over_email.data == "true",
        contact_email=form.contact_email.data,
        contact_phone=form.contact_phone.data,
        contact_textphone=form.contact_textphone.data,
        support_times=form.support_times.data,
        support_days=form.support_days.data,
        instructions_json={"en": form.instructions_en.data or None, "cy": form.instructions_cy.data or None},
        feedback_link=form.feedback_link.data,
        project_name_field_id=form.project_name_field_id.data,
        application_guidance_json={"en": form.application_guidance_en.data or None, "cy": form.application_guidance_cy.data or None},
        guidance_url=form.guidance_url.data,
        all_uploaded_documents_section_available=form.all_uploaded_documents_section_available.data == "true",
        application_fields_download_available=form.application_fields_download_available.data == "true",
        display_logo_on_pdf_exports=form.display_logo_on_pdf_exports.data == "true",
        mark_as_complete_enabled=form.mark_as_complete_enabled.data == "true",
        is_expression_of_interest=form.is_expression_of_interest.data == "true",
        feedback_survey_config={
            "has_feedback_survey": form.feedback_survey_config.data,
            "has_section_feedback": False,
            "is_feedback_survey_optional": False,
            "is_section_feedback_optional": False,
        },
        eligibility_config={"has_eligibility": form.eligibility_config.data},
        eoi_decision_schema={"en": form.eoi_decision_schema_en.data or None, "cy": form.eoi_decision_schema_cy.data or None},
    )
    add_round(new_round)


@build_fund_bp.route("/preview/<form_id>", methods=["GET"])
def preview_form(form_id):
    """
    Generates the form json for a chosen form, does not persist this, but publishes it to the form runner using the
    'runner_publish_name' of that form. Returns a redirect to that form in the form-runner
    """
    form = get_form_by_id(form_id)
    form_json = build_form_json(form)
    form_id = form.runner_publish_name

    try:
        publish_response = requests.post(
            url=f"{Config.FORM_RUNNER_URL}/publish", json={"id": form_id, "configuration": form_json}
        )
        if not str(publish_response.status_code).startswith("2"):
            return "Error during form publish", 500
    except Exception as e:
        return f"unable to publish form: {str(e)}", 500
    return redirect(f"{Config.FORM_RUNNER_URL_REDIRECT}/{form_id}")


@build_fund_bp.route("/download/<form_id>", methods=["GET"])
def download_form_json(form_id):
    """
    Generates form json for the selected form and returns it as a file download
    """
    form = get_form_by_id(form_id)
    form_json = build_form_json(form)

    return Response(
        response=json.dumps(form_json),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename=form-{randint(0,999)}.json"},  # nosec B311
    )


@build_fund_bp.route("/fund/round/<round_id>/all_questions", methods=["GET"])
def view_all_questions(round_id):
    """
    Generates the form data for all sections in the selected round, then uses that to generate the 'All Questions'
    data for that round and returns that to render in a template.
    """
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    sections_in_round = round.sections
    section_data = []
    for section in sections_in_round:
        forms = [{"name": form.runner_publish_name, "form_data": build_form_json(form)} for form in section.forms]
        section_data.append({"section_title": section.name_in_apply_json["en"], "forms": forms})

    print_data = generate_print_data_for_sections(
        section_data,
        lang="en",
    )
    html = print_html(print_data)
    return render_template(
        "view_questions.html",
        round=round,
        fund=fund,
        question_html=html,
        title=f"All Questions for {fund.short_name} - {round.short_name}",
    )


@build_fund_bp.route("/fund/round/<round_id>/all_questions/<form_id>", methods=["GET"])
def view_form_questions(round_id, form_id):
    """
    Generates the form data for this form, then uses that to generate the 'All Questions'
    data for that form and returns that to render in a template.
    """
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    form = get_form_by_id(form_id=form_id)
    section_data = [
        {
            "section_title": f"Preview of form [{form.name_in_apply_json['en']}]",
            "forms": [{"name": form.runner_publish_name, "form_data": build_form_json(form)}],
        }
    ]

    print_data = generate_print_data_for_sections(
        section_data,
        lang="en",
    )
    html = print_html(print_data, True)
    return render_template(
        "view_questions.html", round=round, fund=fund, question_html=html, title=form.name_in_apply_json["en"]
    )


def create_export_zip(directory_to_zip, zip_file_name) -> str:
    # Output zip file path (temporary)
    output_zip_path = Config.TEMP_FILE_PATH / zip_file_name

    # Create a zip archive of the directory
    shutil.make_archive(base_name=output_zip_path, format="zip", root_dir=directory_to_zip)
    return f"{output_zip_path}.zip"


@build_fund_bp.route("/create_export_files/<round_id>", methods=["GET"])
def create_export_files(round_id):
    generate_form_jsons_for_round(round_id)
    generate_all_round_html(round_id)
    generate_config_for_round(round_id)
    round_short_name = get_round_by_id(round_id).short_name

    output_zip_path = create_export_zip(
        directory_to_zip=Config.TEMP_FILE_PATH / round_short_name, zip_file_name=round_short_name
    )

    # Ensure the file is removed after sending it
    @after_this_request
    def remove_file(response):
        os.remove(output_zip_path)
        return response

    # Return the zipped folder for the user to download
    return send_file(output_zip_path, as_attachment=True, download_name=f"{round_short_name}.zip")
