import os
import secrets
import shutil
import string

from flask import (
    Blueprint,
    after_this_request,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from app.all_questions.metadata_utils import generate_print_data_for_sections
from app.blueprints.application.forms import SectionForm
from app.blueprints.application.services import create_export_zip
from app.db.queries.application import (
    delete_form_from_section,
    delete_section_from_round,
    get_all_template_forms,
    get_form_by_id,
    get_section_by_id,
    insert_new_section,
    move_form_down,
    move_form_up,
    move_section_down,
    move_section_up,
    update_section,
)
from app.db.queries.clone import clone_single_form
from app.db.queries.fund import get_fund_by_id
from app.db.queries.round import get_round_by_id
from app.export_config.generate_all_questions import print_html
from app.export_config.generate_assessment_config import (
    generate_assessment_config_for_round,
)
from app.export_config.generate_form import build_form_json
from app.export_config.generate_fund_round_config import generate_config_for_round
from app.export_config.generate_fund_round_form_jsons import (
    generate_form_jsons_for_round,
)
from app.export_config.generate_fund_round_html import generate_all_round_html
from config import Config

INDEX_BP_DASHBOARD = "index_bp.dashboard"

application_bp = Blueprint(
    "application_bp",
    __name__,
    url_prefix="/rounds",
    template_folder="templates",
)


@application_bp.route("/<round_id>/sections")
def build_application(round_id):
    """
    Renders a template displaying application configuration info for the chosen round
    """
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    breadcrumb_items = [
        {"text": "Home", "href": url_for(INDEX_BP_DASHBOARD)},
        {"text": fund.name_json["en"], "href": url_for("fund_bp.view_fund", fund_id=fund.fund_id)},
        {"text": round.title_json["en"], "href": "#"},
    ]
    return render_template("build_application.html", round=round, fund=fund, breadcrumb_items=breadcrumb_items)


@application_bp.route("/<round_id>/sections/all-questions", methods=["GET"])
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


@application_bp.route("/<round_id>/sections/create_export_files", methods=["GET"])
def create_export_files(round_id):
    round_short_name = get_round_by_id(round_id).short_name
    # Construct the path to the output directory relative to this file's location
    random_post_fix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    base_output_dir = Config.TEMP_FILE_PATH / f"{round_short_name}-{random_post_fix}"
    generate_form_jsons_for_round(round_id, base_output_dir)
    generate_all_round_html(round_id, base_output_dir)
    fund_config, round_config = generate_config_for_round(round_id, base_output_dir)
    generate_assessment_config_for_round(fund_config, round_config, base_output_dir)
    output_zip_path = create_export_zip(
        directory_to_zip=base_output_dir, zip_file_name=round_short_name, random_post_fix=random_post_fix
    )

    # Ensure the file is removed after sending it
    @after_this_request
    def remove_file(response):
        os.remove(output_zip_path)
        shutil.rmtree(base_output_dir)
        return response

    # Return the zipped folder for the user to download
    return send_file(output_zip_path, as_attachment=True, download_name=f"{round_short_name}.zip")


@application_bp.route("/<round_id>/sections/create", methods=["GET", "POST"])
@application_bp.route("/<round_id>/sections/<section_id>", methods=["GET", "POST"])
def section(round_id, section_id=None):
    round_obj = get_round_by_id(round_id)
    fund_obj = get_fund_by_id(round_obj.fund_id)
    form: SectionForm = SectionForm()
    form.round_id.data = round_id
    params = {
        "round_id": str(round_id),
    }
    existing_section = None
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
        return redirect(url_for("application_bp.build_application", round_id=round_obj.round_id))
    if section_id:
        existing_section = get_section_by_id(section_id)
        form.section_id.data = section_id
        form.name_in_apply_en.data = existing_section.name_in_apply_json["en"]
        params["forms_in_section"] = existing_section.forms
        params["available_template_forms"] = [
            {"text": f"{f.template_name} - {f.name_in_apply_json['en']}", "value": str(f.form_id)}
            for f in get_all_template_forms()
        ]

    params["breadcrumb_items"] = [
        {"text": "Home", "href": url_for(INDEX_BP_DASHBOARD)},
        {"text": fund_obj.name_json["en"], "href": url_for("fund_bp.view_fund", fund_id=fund_obj.fund_id)},
        {
            "text": round_obj.title_json["en"],
            "href": url_for("application_bp.build_application", round_id=round_obj.round_id),
        },
        {"text": existing_section.name_in_apply_json["en"] if existing_section else "Add Section", "href": "#"},
    ]
    return render_template("section.html", form=form, **params)


@application_bp.route("/<round_id>/sections/<section_id>/delete", methods=["GET"])
def delete_section(round_id, section_id):
    delete_section_from_round(round_id=round_id, section_id=section_id, cascade=True)
    return redirect(url_for("application_bp.build_application", round_id=round_id))


@application_bp.route("/<round_id>/sections/<section_id>/move-up", methods=["GET"])
def move_section_up_route(round_id, section_id):
    move_section_up(round_id=round_id, section_id=section_id)
    return redirect(url_for("application_bp.build_application", round_id=round_id))


@application_bp.route("/<round_id>/sections/<section_id>/move-down", methods=["GET"])
def move_section_down_route(round_id, section_id):
    move_section_down(round_id=round_id, section_id=section_id)
    return redirect(url_for("application_bp.build_application", round_id=round_id))


@application_bp.route("/<round_id>/sections/<section_id>/forms/add", methods=["POST"])
def add_form(round_id, section_id):
    template_id = request.form.get("template_id")
    section = get_section_by_id(section_id=section_id)
    new_section_index = max(len(section.forms) + 1, 1)
    clone_single_form(form_id=template_id, new_section_id=section_id, section_index=new_section_index)
    return redirect(url_for("application_bp.section", round_id=round_id, section_id=section_id))


@application_bp.route("/<round_id>/sections/<section_id>/forms/<form_id>/delete", methods=["GET"])
def delete_form(round_id, section_id, form_id):
    delete_form_from_section(section_id=section_id, form_id=form_id, cascade=True)
    return redirect(url_for("application_bp.section", round_id=round_id, section_id=section_id))


@application_bp.route("/<round_id>/sections/<section_id>/forms/<form_id>/move-up", methods=["GET"])
def move_form_up_route(round_id, section_id, form_id):
    move_form_up(section_id=section_id, form_id=form_id)
    return redirect(url_for("application_bp.section", round_id=round_id, section_id=section_id))


@application_bp.route("/<round_id>/sections/<section_id>/forms/<form_id>/move-down", methods=["GET"])
def move_form_down_route(round_id, section_id, form_id):
    move_form_down(section_id=section_id, form_id=form_id)
    return redirect(url_for("application_bp.section", round_id=round_id, section_id=section_id))


@application_bp.route("/<round_id>/sections/<section_id>/forms/<form_id>/all-questions", methods=["GET"])
def view_form_questions(round_id, section_id, form_id):
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
