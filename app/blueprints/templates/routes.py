import json

from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import url_for
from werkzeug.utils import secure_filename

from app.blueprints.fund_builder.forms.templates import TemplateUploadForm
from app.db.queries.application import get_all_template_forms
from app.db.queries.application import get_all_template_sections
from app.db.queries.application import get_form_by_template_name

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


@template_bp.route("/view", methods=["GET", "POST"])
def view_templates():
    sections = get_all_template_sections()
    forms = get_all_template_forms()
    form = TemplateUploadForm()
    if form.validate_on_submit():
        template_name = form.template_name.data
        file = form.file.data
        if get_form_by_template_name(template_name):
            form.error = "Template name already exists"
            return render_template("view_templates.html", sections=sections, forms=forms, uploadform=form)

        if file:
            try:
                secure_filename(file.filename)
                file_data = file.read().decode("utf-8")
                form_data = json.loads(file_data)
                json_import(data=form_data, template_name=template_name)
            except Exception as e:
                print(e)
                form.error = "Invalid file: Please upload valid JSON file"
                return render_template("view_templates.html", sections=sections, forms=forms, uploadform=form)

        return redirect(url_for("template_bp.view_templates"))

    return render_template("view_templates.html", sections=sections, forms=forms, uploadform=form)
