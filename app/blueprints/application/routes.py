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
from app.blueprints.application.forms import SectionForm, SelectApplicationForm
from app.blueprints.application.services import create_export_zip
from app.db.queries.application import (
    delete_form_from_section,
    delete_section_from_round,
    get_form_by_id,
    get_section_by_id,
    insert_new_form,
    insert_new_section,
    move_form_down,
    move_form_up,
    move_section_down,
    move_section_up,
    update_section,
)
from app.db.queries.fund import get_all_funds, get_fund_by_id
from app.db.queries.round import get_round_by_id, update_round
from app.export_config.generate_all_questions import generate_html
from app.export_config.generate_assessment_config import (
    generate_assessment_config_for_round,
)
from app.export_config.generate_fund_round_config import generate_config_for_round
from app.export_config.generate_fund_round_html import generate_all_round_html
from app.shared.form_store_api import FormStoreAPIService
from app.shared.forms import DeleteConfirmationForm, SelectFundForm
from app.shared.helpers import flash_message
from config import Config

INDEX_BP_DASHBOARD = "index_bp.dashboard"

application_bp = Blueprint(
    "application_bp",
    __name__,
    url_prefix="/rounds",
    template_folder="templates",
)


@application_bp.route("/sections/select-grant", methods=["GET", "POST"])
def select_fund():
    """
    Intermediary page to select a Fund before building an Application.
    """
    form = SelectFundForm()
    choices = [("", "Select a grant")]
    for fund in get_all_funds():
        choices.append((str(fund.fund_id), fund.short_name + " - " + fund.name_json["en"]))
    form.fund_id.choices = choices
    if form.validate_on_submit():
        return redirect(url_for("application_bp.select_application", fund_id=form.fund_id.data))
    select_items = [{"value": value, "text": text} for value, text in choices]
    return render_template(
        "select_fund.html", form=form, select_items=select_items, cancel_url=url_for(INDEX_BP_DASHBOARD)
    )


@application_bp.route("/sections/select-application", methods=["GET", "POST"])
def select_application():
    """
    Intermediary page to select an Application before managing its tasklist.
    """
    fund_id = request.args.get("fund_id")
    if not fund_id:
        raise ValueError("Fund ID is required to manage an application")
    fund = get_fund_by_id(fund_id)
    form = SelectApplicationForm(fund)
    if form.validate_on_submit():
        return redirect(url_for("application_bp.build_application", round_id=form.round_id.data))
    return render_template("select_application.html", form=form, fund=fund)


@application_bp.route("/<round_id>/sections")
def build_application(round_id):
    """
    Renders a template displaying application configuration info for the chosen round
    """
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    back_link = (
        url_for("round_bp.round_details", round_id=round.round_id)
        if request.args.get("action") == "application_details"
        else url_for("round_bp.view_all_rounds")
    )

    # Call Pre-Award API to get display names for forms
    api_service = FormStoreAPIService()
    published_forms = api_service.get_published_forms()
    url_path_to_display_name = {pf.url_path: pf.display_name for pf in published_forms}
    for section in round.sections:
        for local_form in section.forms:
            # Dynamically assigning the undefined display_name attribute to the Form SQLAlchemy model for simplicity
            local_form.display_name = url_path_to_display_name.get(local_form.url_path, local_form.url_path)

    return render_template("build_application.html", round=round, fund=fund, back_link=back_link)


@application_bp.route("/<round_id>/mark-complete", methods=["GET"])
def mark_application_complete(round_id):
    """
    Marks an application as complete
    """
    round_ = get_round_by_id(round_id)
    round_.status = "Complete"
    update_round(round_)
    return redirect(url_for("application_bp.application_complete", round_id=round_id))


@application_bp.route("/<round_id>/complete", methods=["GET"])
def application_complete(round_id):
    """
    Shows the confirmation page after marking an application as complete
    """
    round_ = get_round_by_id(round_id)
    fund = get_fund_by_id(round_.fund_id)
    return render_template("application_complete.html", round=round_, fund=fund)


@application_bp.route("/<round_id>/mark-in-progress", methods=["GET"])
def mark_application_in_progress(round_id):
    """
    Sets an application status back to 'In progress'
    """
    round_ = get_round_by_id(round_id)
    round_.status = "In progress"
    update_round(round_)
    return redirect(url_for("application_bp.build_application", round_id=round_id))


@application_bp.route("/<round_id>/sections/all-questions", methods=["GET"])
def view_all_questions(round_id):
    """
    Generates the form data for all sections in the selected round, then uses that to generate the 'All Questions'
    data for that round and returns that to render in a template.
    """
    api_service = FormStoreAPIService()
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    sections_in_round = round.sections
    section_data = []
    for section in sections_in_round:
        forms = []
        for form in section.forms:
            configuration = api_service.get_published_form(form.url_path)
            forms.append({"name": form.url_path, "form_data": configuration})
        section_data.append({"section_title": section.name_in_apply_json["en"], "forms": forms})

    print_data = generate_print_data_for_sections(
        section_data,
        lang="en",
    )
    html = generate_html(print_data)
    return render_template(
        "view_questions.html",
        round=round,
        fund=fund,
        question_html=html,
        title=f"All Questions for {fund.short_name} - {round.short_name}",
        all_questions_view=True,
    )


@application_bp.route("/<round_id>/sections/create_export_files", methods=["GET"])
def create_export_files(round_id):
    round_short_name = get_round_by_id(round_id).short_name
    # Construct the path to the output directory relative to this file's location
    random_post_fix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(5))
    base_output_dir = Config.TEMP_FILE_PATH / f"{round_short_name}-{random_post_fix}"
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
    form: SectionForm = SectionForm()
    form.round_id.data = round_id
    params = {
        "round_id": str(round_id),
    }
    if form.validate_on_submit():
        if not form.add_form.data:
            count_existing_sections = len(round_obj.sections)
            if form.section_id.data:
                update_section(
                    form.section_id.data,
                    {
                        "name_in_apply_json": {"en": form.name_in_apply_en.data},
                    },
                )
                flash_message("Section updated")
            else:
                insert_new_section(
                    {
                        "round_id": form.round_id.data,
                        "name_in_apply_json": {"en": form.name_in_apply_en.data},
                        "index": max(count_existing_sections + 1, 1),
                    }
                )
                flash_message("Section added")
            return redirect(url_for("application_bp.build_application", round_id=round_obj.round_id))

        section = get_section_by_id(section_id=section_id)
        new_section_index = max(len(section.forms) + 1, 1)
        insert_new_form(section_id=section.section_id, url_path=form.template_id.data, section_index=new_section_index)
        form.template_id.data = ""  # Reset the template_id field to default after adding

    if section_id:
        existing_section = get_section_by_id(section_id)
        form.section_id.data = section_id
        form.name_in_apply_en.data = existing_section.name_in_apply_json["en"]
        params["forms_in_section"] = existing_section.forms

    # Get forms from Pre-Award API to show in "Add a task" drop-down
    choices = [("", "Select a template")]
    url_path_to_display_name = {}
    api_service = FormStoreAPIService()
    published_forms = api_service.get_published_forms()
    for published_form in published_forms:
        url_path = published_form.url_path
        display_name = published_form.display_name
        if display_name:
            choices.append((url_path, f"{display_name} ({url_path})"))
        url_path_to_display_name[url_path] = display_name
    choices.sort(key=lambda c: c[1])
    form.template_id.choices = choices

    # Match form display names from Pre-Award API to local forms to show display names in "Tasks in this section"
    for local_form in params.get("forms_in_section", []):
        # Dynamically assigning the undefined display_name attribute to the Form SQLAlchemy model for simplicity
        local_form.display_name = url_path_to_display_name.get(local_form.url_path, local_form.url_path)

    return render_template("section.html", form=form, **params)


@application_bp.route("/<round_id>/sections/<section_id>/delete", methods=["GET", "POST"])  # Sensitive
def delete_section(round_id, section_id):
    form = DeleteConfirmationForm()

    if form.validate_on_submit():  # If user confirms deletion
        delete_section_from_round(round_id=round_id, section_id=section_id, cascade=True)
        return redirect(url_for("application_bp.build_application", round_id=round_id))

    # Render confirmation page
    return render_template(
        "delete_confirmation.html",
        form=form,
        cancel_url=url_for("application_bp.section", round_id=round_id, section_id=section_id),
        delete_action_item="section",
    )


@application_bp.route("/<round_id>/sections/<section_id>/move-up", methods=["GET"])
def move_section_up_route(round_id, section_id):
    move_section_up(round_id=round_id, section_id=section_id)
    return redirect(url_for("application_bp.build_application", round_id=round_id))


@application_bp.route("/<round_id>/sections/<section_id>/move-down", methods=["GET"])
def move_section_down_route(round_id, section_id):
    move_section_down(round_id=round_id, section_id=section_id)
    return redirect(url_for("application_bp.build_application", round_id=round_id))


@application_bp.route("/<round_id>/sections/<section_id>/forms/<form_id>/delete", methods=["GET"])
def delete_form(round_id, section_id, form_id):
    delete_form_from_section(section_id=section_id, form_id=form_id)
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
    api_service = FormStoreAPIService()
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    form = get_form_by_id(form_id=form_id)
    configuration = api_service.get_published_form(form.url_path)
    start_page = next(
        (p for p in configuration["pages"] if p.get("controller") and p["controller"].endswith("start.js")), None
    )
    section_data = [
        {
            "section_title": f"Preview of form [{form.url_path}]",
            "forms": [{"name": form.url_path, "form_data": configuration}],
        }
    ]

    print_data = generate_print_data_for_sections(
        section_data,
        lang="en",
    )
    html = generate_html(print_data, False)
    return render_template(
        "view_questions.html",
        round=round,
        fund=fund,
        question_html=html,
        title=start_page["title"],
        all_questions_view=False,
    )
