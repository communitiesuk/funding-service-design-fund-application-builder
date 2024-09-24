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
from app.db.models.round import Round
from app.db.queries.application import clone_single_form
from app.db.queries.application import clone_single_round
from app.db.queries.application import delete_form_from_section
from app.db.queries.application import delete_section_from_round
from app.db.queries.application import get_all_template_forms
from app.db.queries.application import get_form_by_id
from app.db.queries.application import get_section_by_id
from app.db.queries.application import insert_new_section
from app.db.queries.application import update_section
from app.db.queries.fund import add_fund
from app.db.queries.fund import get_all_funds
from app.db.queries.fund import get_fund_by_id
from app.db.queries.round import add_round
from app.db.queries.round import get_round_by_id
from app.export_config.generate_all_questions import print_html
from app.export_config.generate_form import build_form_json
from app.export_config.generate_fund_round_config import (
    generate_application_display_config,
)
from app.export_config.generate_fund_round_config import generate_fund_config
from app.export_config.generate_fund_round_form_jsons import (
    generate_form_jsons_for_round,
)
from app.export_config.generate_fund_round_html import generate_all_round_html
from config import Config

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
    if request.args.get("action") == "remove":
        delete_section_from_round(round_id=round_id, section_id=request.args.get("section_id"), cascade=True)
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
        {"text": fund_obj.name_json["en"], "href": url_for("build_fund_bp.view_fund", fund_id=fund_obj.fund_id)},
        {
            "text": round_obj.title_json["en"],
            "href": url_for("build_fund_bp.build_application", fund_id=fund_obj.fund_id, round_id=round_obj.round_id),
        },
        {"text": existing_section.name_in_apply_json["en"] if existing_section else "Add Section", "href": "#"},
    ]
    return render_template("section.html", form=form, **params)


@build_fund_bp.route("/fund/round/<round_id>/section/<section_id>/forms", methods=["POST"])
def configure_forms_in_section(round_id, section_id):
    if request.method == "POST":
        if request.args.get("action") == "remove":
            form_id = request.args.get("form_id")
            delete_form_from_section(section_id=section_id, form_id=form_id, cascade=True)
        else:
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
        {"text": "Home", "href": url_for("build_fund_bp.index")},
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
def fund():
    """
    Renders a template to allow a user to add a fund, when saved validates the form data and saves to DB
    """
    form: FundForm = FundForm()
    if form.validate_on_submit():
        add_fund(
            Fund(
                name_json={"en": form.name_en.data},
                title_json={"en": form.title_en.data},
                description_json={"en": form.description_en.data},
                welsh_available=form.welsh_available.data == "true",
                short_name=form.short_name.data,
                audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
            )
        )
        flash(f"Saved fund {form.name_en.data}")
        return redirect(url_for("build_fund_bp.index"))

    return render_template("fund.html", form=form)


@build_fund_bp.route("/round", methods=["GET", "POST"])
def round():
    """
    Renders a template to select a fund and add a round to that fund. If saved, validates the round form data
    and saves to DB
    """
    all_funds = get_all_funds()
    form: RoundForm = RoundForm()
    if form.validate_on_submit():
        add_round(
            Round(
                fund_id=form.fund_id.data,
                audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
                title_json={"en": form.title_en.data},
                short_name=form.short_name.data,
                opens=get_datetime(form.opens),
                deadline=get_datetime(form.deadline),
                assessment_start=get_datetime(form.assessment_start),
                reminder_date=get_datetime(form.reminder_date),
                assessment_deadline=get_datetime(form.assessment_deadline),
                prospectus_link=form.prospectus_link.data,
                privacy_notice_link=form.privacy_notice_link.data,
                contact_us_banner_json={"en": form.contact_us_banner_json.data, "cy": None},
                reference_contact_page_over_email=form.reference_contact_page_over_email.data == "true",
                contact_email=form.contact_email.data,
                contact_phone=form.contact_phone.data,
                contact_textphone=form.contact_textphone.data,
                support_times=form.support_times.data,
                support_days=form.support_days.data,
                instructions_json={"en": form.instructions_json.data, "cy": None},
                feedback_link=form.feedback_link.data,
                project_name_field_id=form.project_name_field_id.data,
                application_guidance_json={"en": form.application_guidance_json.data, "cy": None},
                guidance_url=form.guidance_url.data,
                all_uploaded_documents_section_available=form.all_uploaded_documents_section_available.data == "true",
                application_fields_download_available=form.application_fields_download_available.data == "true",
                display_logo_on_pdf_exports=form.display_logo_on_pdf_exports.data == "true",
                mark_as_complete_enabled=form.mark_as_complete_enabled.data == "true",
                is_expression_of_interest=form.is_expression_of_interest.data == "true",
                feedback_survey_config=form.feedback_survey_config.data,
                eoi_decision_schema=form.eoi_decision_schema.data,
            )
        )

        flash(f"Saved round {form.title_en.data}")
        return redirect(url_for("build_fund_bp.index"))

    return render_template(
        "round.html",
        form=form,
        all_funds=all_funds_as_govuk_select_items(all_funds),
    )


@build_fund_bp.route("/preview/<form_id>", methods=["GET"])
def preview_form(form_id):
    """
    Generates the form json for a chosen form, does not persist this, but publishes it to the form runner using the
    'runner_publish_name' of that form. Returns a redirect to that form in the form-runner
    """
    form = get_form_by_id(form_id)
    form_json = build_form_json(form)

    try:
        publish_response = requests.post(
            url=f"{Config.FORM_RUNNER_URL}/publish", json={"id": form.runner_publish_name, "configuration": form_json}
        )
        if not str(publish_response.status_code).startswith("2"):
            return "Error during form publish", 500
    except Exception as e:
        return f"unable to publish form: {str(e)}", 500
    return redirect(f"{Config.FORM_RUNNER_URL_REDIRECT}/{form.runner_publish_name}")


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


@build_fund_bp.route("/create_export_files/<round_id>", methods=["GET"])
def create_export_files(round_id):
    generate_form_jsons_for_round(round_id)
    generate_all_round_html(round_id)
    generate_application_display_config(round_id)
    generate_fund_config(round_id)
    round_short_name = get_round_by_id(round_id).short_name

    # Directory to zip
    directory_to_zip = f"app/export_config/output/{round_short_name}/"
    # Output zip file path (temporary)
    output_zip_path = f"app/export_config/output/{round_short_name}.zip"

    # Create a zip archive of the directory
    shutil.make_archive(output_zip_path.replace(".zip", ""), "zip", directory_to_zip)

    # Ensure the file is removed after sending it
    @after_this_request
    def remove_file(response):
        os.remove(output_zip_path)
        return response

    # Return the zipped folder for the user to download
    return send_file(output_zip_path, as_attachment=True, download_name=f"{round_short_name}.zip")
