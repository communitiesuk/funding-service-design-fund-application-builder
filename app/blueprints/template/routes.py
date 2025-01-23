import json

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.blueprints.index.routes import INDEX_BP_DASHBOARD
from app.blueprints.template.forms import TemplateCreateForm, TemplateUpdateForm
from app.blueprints.template.services import build_rows, json_import
from app.db.queries.application import (
    delete_form,
    get_all_template_forms,
    get_form_by_id,
    get_form_by_template_name,
    update_form,
)
from app.export_config.helpers import human_to_kebab_case
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

    return render_template("view_all_templates.html", **params, form_designer_url=form_designer_url)


@template_bp.route("/create", methods=["GET", "POST"])
def create_template():
    form = TemplateCreateForm()
    params = {"form": form}
    if request.method == "GET":
        # Render the form on the initial GET request
        return render_template("template.html", form=form)
    if form.validate_on_submit():
        template_name = form.template_name.data
        tasklist_name = form.tasklist_name.data
        file = form.file.data
        if get_form_by_template_name(template_name):
            form.template_name.errors.append("Template name already exists")
            return render_template("template.html", **params)
        if file:
            try:
                file_data = file.read().decode("utf-8")
                form_data = json.loads(file_data)
                form_data["name"] = tasklist_name
                created_form = json_import(
                    data=form_data, template_name=template_name, filename=human_to_kebab_case(f"{tasklist_name}.json")
                )
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
                return render_template("template.html", **params)
        return redirect(url_for("template_bp.view_templates"))
    return render_template("template.html", **params)


@template_bp.route("/<uuid:form_id>/questions", methods=["GET"])
def template_questions(form_id):
    form = get_form_by_id(form_id)
    return render_template("view_template_questions.html", form=form)


@template_bp.route("/<uuid:form_id>", methods=["GET"])
def template_details(form_id):
    form_obj = TemplateUpdateForm()
    form = get_form_by_id(form_id)
    return render_template("template_details.html", form=form, form_obj=form_obj)


@template_bp.route("/<uuid:form_id>/edit", methods=["GET", "POST"])
def edit_template(form_id):
    form = TemplateUpdateForm()
    params = {"form": form}
    existing_form = get_form_by_id(form_id=form_id)
    if request.method == "GET":
        form.form_id.data = form_id
        form.template_name.data = existing_form.template_name
        form.tasklist_name.data = existing_form.name_in_apply_json["en"]
        form.file.data = human_to_kebab_case(f"{existing_form.name_in_apply_json['en']}.json")
        params.update({"template_name": existing_form.template_name})
        return render_template("template.html", **params)
    if form.validate_on_submit():
        update_form(
            form_id=form_id,
            new_form_config={
                "name_in_apply_json": {"en": form.tasklist_name.data},
                "template_name": form.template_name.data,
            },
        )
        if form.file and form.file.data is not None:
            delete_form(form_id=form_id, cascade=True)
            file_data = form.file.data.read().decode("utf-8")
            form_data = json.loads(file_data)
            form_data["name"] = form.tasklist_name.data
            created_form = json_import(
                data=form_data,
                template_name=form.template_name.data,
                filename=human_to_kebab_case(f"{form.tasklist_name.data}.json"),
            )
            flash(f"Updated template {form.template_name.data}")
            if form.save_and_continue.data:
                return redirect(url_for("template_bp.template_details", form_id=created_form.form_id))
            return redirect(url_for("index_bp.dashboard"))
        flash(f"Updated template {form.template_name.data}")
        if form.save_and_continue.data:
            return redirect(url_for("template_bp.template_details", form_id=form_id))
        return redirect(url_for("index_bp.dashboard"))
    params.update({"template_name": existing_form.template_name})
    return render_template("template.html", **params)


@template_bp.route("/<form_id>/delete", methods=["GET"])
def delete_template(form_id):
    delete_form(form_id=form_id, cascade=True)
    return redirect(url_for("template_bp.view_templates"))
