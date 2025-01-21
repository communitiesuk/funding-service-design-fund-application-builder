import json

from flask import Blueprint, current_app, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from app.blueprints.index.routes import INDEX_BP_DASHBOARD
from app.blueprints.template.forms import TemplateCreateForm, TemplateFormForm
from app.blueprints.template.services import build_rows, json_import
from app.db.queries.application import (
    delete_form,
    get_all_template_forms,
    get_form_by_id,
    get_form_by_template_name,
    update_form,
)
from app.shared.helpers import flash_message
from app.shared.table_pagination import GovUKTableAndPagination

template_bp = Blueprint(
    "template_bp",
    __name__,
    url_prefix="/templates",
    template_folder="templates",
)


@template_bp.route("", methods=["GET"])
def view_templates():
    forms = get_all_template_forms()
    form_designer_url = current_app.config["FORM_DESIGNER_URL_REDIRECT"] + "/app"
    params = GovUKTableAndPagination(
        table_header=[
            {"text": "Template name"},
            {"text": "Task name"},
            {"text": ""},
        ],
        table_rows=build_rows(forms),
        current_page=int(request.args.get("page", 1)),
    ).__dict__

    return render_template("view_templates.html", **params, form_designer_url=form_designer_url)


@template_bp.route("/create", methods=["GET", "POST"])
def create_template():
    form = TemplateCreateForm()
    params = {"form": form}
    if request.method == "GET":
        # Render the form on the initial GET request
        return render_template("create_template.html", form=form)
    if form.validate_on_submit():
        template_name = form.template_name.data
        tasklist_name = form.tasklist_name.data
        file = form.file.data
        if get_form_by_template_name(template_name):
            form.template_name.errors.append("Template name already exists")
            return render_template("create_template.html", **params)
        if file:
            try:
                filename = secure_filename(file.filename)
                file_data = file.read().decode("utf-8")
                form_data = json.loads(file_data)
                form_data["name"] = tasklist_name
                created_form = json_import(data=form_data, template_name=template_name, filename=filename)
                flash_message(
                    message="Template uploaded",
                    href=url_for("template_bp.template_details", form_id=created_form.form_id),
                    href_display_name=template_name,
                )
                if request.form.get("action") == "return_home":
                    return redirect(url_for(INDEX_BP_DASHBOARD))
            except Exception as e:
                print(e)
                form.file.errors.append("Please upload valid JSON file")
                return render_template("create_template.html", **params)
        return redirect(url_for("template_bp.view_templates"))
    return render_template("create_template.html", **params)


@template_bp.route("/<uuid:form_id>", methods=["GET"])
def template_details(form_id):
    form = get_form_by_id(form_id)
    return render_template("template_details.html", form=form)


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
    return render_template("edit_form_template.html", **params)


@template_bp.route("/<form_id>/delete", methods=["GET"])
def delete_template(form_id):
    delete_form(form_id=form_id, cascade=True)
    return redirect(url_for("template_bp.view_templates"))
