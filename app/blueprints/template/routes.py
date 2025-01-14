import json

from flask import Blueprint, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from app.blueprints.template.forms import TemplateFormForm, TemplateUploadForm
from app.blueprints.template.services import build_rows, json_import
from app.db.queries.application import (
    delete_form,
    get_all_template_forms,
    get_all_template_sections,
    get_form_by_id,
    get_form_by_template_name,
    update_form,
)
from app.shared.generic_table_page import GenericTablePage
from app.shared.helpers import error_formatter
from config import Config

template_bp = Blueprint(
    "template_bp",
    __name__,
    url_prefix="/templates",
    template_folder="templates",
)


@template_bp.route("", methods=["GET", "POST"])
def view_templates():
    sections = get_all_template_sections()
    forms = get_all_template_forms()
    form = TemplateUploadForm()
    params = {"sections": sections, "forms": forms, "uploadform": form}
    detail_description_html = """
    <p>You should use existing templates for standard application questions. For example, all
    grant applications should collect organisation and risk information in the same way.</p>
    <p>If your application needs questions specific to the grant, you can create a new template by:</p>
    <ol>
      <li>designing the template in Form Designer</li>
      <li>downloading the template</li>
      <li>uploading the template to Fund application builder</li>
    </ol>
    """
    params.update(
        GenericTablePage(
            page_heading="Templates",
            page_description="Follow the step-by-step instructions to create a new grant application.",
            detail_text="Using templates in applications",
            detail_description_html=detail_description_html,
            button_text="Upload template",
            button_url="#",
            table_header=[
                {"text": "Template name"},
                {"text": "Task name"},
                {"text": ""},
            ],
            table_rows=build_rows(forms),
            current_page=int(request.args.get("page", 1)),
            page_description_link_text="Form Designer (opens in a new tab).",
            page_description_link_url=f"{Config.FORM_RUNNER_URL_REDIRECT}/app",
        ).__dict__
    )
    if form.validate_on_submit():
        template_name = form.template_name.data
        file = form.file.data
        if get_form_by_template_name(template_name):
            form.error = "Template name already exists"
            return render_template("view_templates.html", **params)

        if file:
            try:
                filename = secure_filename(file.filename)
                file_data = file.read().decode("utf-8")
                form_data = json.loads(file_data)
                json_import(data=form_data, template_name=template_name, filename=filename)
            except Exception as e:
                print(e)
                form.error = "Invalid file: Please upload valid JSON file"
                return render_template("view_templates.html", **params)

        return redirect(url_for("template_bp.view_templates"))

    error = None
    if "uploadform" in params:
        error = error_formatter(params["uploadform"])
    return render_template("view_templates.html", **params, error=error)


@template_bp.route("/<form_id>", methods=["GET", "POST"])
def edit_template(form_id):
    template_form = TemplateFormForm()
    if template_form.validate_on_submit():
        update_form(
            form_id=form_id,
            new_form_config={
                "runner_publish_name": template_form.url_path.data,
                "name_in_apply_json": {"en": template_form.tasklist_name.data},
                "template_name": template_form.template_name.data,
            },
        )
        return redirect(url_for("template_bp.view_templates"))
    existing_form = get_form_by_id(form_id=form_id)
    template_form.form_id.data = form_id
    template_form.template_name.data = existing_form.template_name
    template_form.tasklist_name.data = existing_form.name_in_apply_json["en"]
    template_form.url_path.data = existing_form.runner_publish_name
    params = {"template_form": template_form}
    error = error_formatter(template_form)
    return render_template(
        "edit_form_template.html",
        **params,
        error=error,
    )


@template_bp.route("/<form_id>/delete", methods=["GET"])
def delete_template(form_id):
    delete_form(form_id=form_id, cascade=True)
    return redirect(url_for("template_bp.view_templates"))
