from flask import Blueprint
from flask import redirect
from flask import url_for
from flask import render_template
from wtforms import ValidationError
from app.db.queries.application import get_all_template_forms
from app.db.queries.application import get_all_template_sections
from app.blueprints.fund_builder.forms.templates import TemplateUploadForm
import os
from werkzeug.utils import secure_filename


# Blueprint for routes used by FAB PoC to manage templates
template_bp = Blueprint(
    "template_bp",
    __name__,
    url_prefix="/templates",
    template_folder="templates",
)

file_upload_path = os.path.join(os.path.dirname(__file__), "uplaoded_files")

def json_import(file_path, template_name):
    from app.import_config.load_form_json import load_json_from_file

    load_json_from_file(file_path=file_path, template_name=template_name)


@template_bp.route("/view", methods=["GET", "POST"])
def view_templates():
    sections = get_all_template_sections()
    forms = get_all_template_forms()
    form = TemplateUploadForm()
    if form.validate_on_submit():
        template_name = form.template_name.data
        file = form.file.data
        if not os.path.exists(file_upload_path):
            os.makedirs(file_upload_path)
        if file:
            uploaded_file = secure_filename(file.filename)
            file_path = os.path.join(file_upload_path, uploaded_file)
            file.save(file_path)
            try:
                json_import(file_path=file_path, template_name=template_name)
            except Exception as e:
                print(e)
        return redirect(url_for("template_bp.view_templates"))

    return render_template("view_templates.html", sections=sections, forms=forms, uploadform=form)
