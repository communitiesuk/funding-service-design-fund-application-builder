import json

from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.utils import secure_filename

from app.blueprints.fund_builder.forms.templates import TemplateFormForm
from app.blueprints.fund_builder.forms.templates import TemplateUploadForm
from app.db.models.application_config import Form
from app.db.queries.application import delete_form
from app.db.queries.application import get_all_template_forms
from app.db.queries.application import get_all_template_sections
from app.db.queries.application import get_form_by_id
from app.db.queries.application import get_form_by_template_name
from app.db.queries.application import update_form

# Blueprint for routes used by FAB PoC to manage templates
template_bp = Blueprint(
    "template_bp",
    __name__,
    url_prefix="/templates",
    template_folder="templates",
)


def json_import(data, template_name):
    from app.import_config.load_form_json import load_json_from_file

    load_json_from_file(data=data, template_name=template_name)


def _build_rows(forms: list[Form]) -> list[dict]:
    rows = []
    for form in forms:
        row = [
            {
                "html": "<a class='govuk-link--no-visited-state' "
                f"href='{url_for('build_fund_bp.preview_form', form_id=form.form_id)}'>{form.template_name}</a>"
            },
            {"text": form.name_in_apply_json["en"]},
            {"text": form.runner_publish_name},
            {
                "html": "<a class='govuk-link--no-visited-state' href='"
                f"{url_for('template_bp.edit_form_template', form_id=form.form_id, action='remove')}'>Delete</a> &nbsp;"
                "<a class='govuk-link--no-visited-state' href='"
                f"{url_for('template_bp.edit_form_template', form_id=form.form_id, action='edit')}'>Rename</a>"
            },
        ]
        rows.append(row)
    return rows


@template_bp.route("/all", methods=["GET", "POST"])
def view_templates():
    sections = get_all_template_sections()
    forms = get_all_template_forms()
    form = TemplateUploadForm()
    params = {
        "sections": sections,
        "forms": forms,
        "form_template_rows": _build_rows(forms),
        "uploadform": form,
        "breadcrumb_items": [
            {"text": "Home", "href": url_for("build_fund_bp.index")},
            {"text": "Manage Templates", "href": "#"},
        ],
    }
    if form.validate_on_submit():
        template_name = form.template_name.data
        file = form.file.data
        if get_form_by_template_name(template_name):
            form.error = "Template name already exists"
            return render_template("view_templates.html", **params)

        if file:
            try:
                secure_filename(file.filename)
                file_data = file.read().decode("utf-8")
                form_data = json.loads(file_data)
                json_import(data=form_data, template_name=template_name)
            except Exception as e:
                print(e)
                form.error = "Invalid file: Please upload valid JSON file"
                return render_template("view_templates.html", **params)

        return redirect(url_for("template_bp.view_templates"))

    return render_template("view_templates.html", **params)


@template_bp.route("/forms/<form_id>", methods=["GET", "POST"])
def edit_form_template(form_id):
    template_form = TemplateFormForm()
    params = {
        "breadcrumb_items": [
            {"text": "Home", "href": url_for("build_fund_bp.index")},
            {"text": "Manage Templates", "href": url_for("template_bp.view_templates")},
            {"text": "Rename Template", "href": "#"},
        ],
    }

    if request.method == "POST":
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
        params["template_form"] = template_form
        return render_template("edit_form_template.html", **params)

    if request.args.get("action") == "remove":
        delete_form(form_id=form_id, cascade=True)
    if request.args.get("action") == "edit":
        existing_form = get_form_by_id(form_id=form_id)
        template_form = TemplateFormForm()
        template_form.form_id.data = form_id
        template_form.template_name.data = existing_form.template_name
        template_form.tasklist_name.data = existing_form.name_in_apply_json["en"]
        template_form.url_path.data = existing_form.runner_publish_name
        params["template_form"] = template_form
        return render_template("edit_form_template.html", **params)

    return redirect(url_for("template_bp.view_templates"))
