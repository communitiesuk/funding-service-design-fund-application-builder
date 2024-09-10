from flask import Blueprint
from flask import render_template

from app.db.queries.application import get_all_template_forms
from app.db.queries.application import get_all_template_sections

# Blueprint for routes used by FAB PoC to manage templates
template_bp = Blueprint(
    "template_bp",
    __name__,
    url_prefix="/templates",
    template_folder="templates",
)


@template_bp.route("/view")
def view_templates():
    sections = get_all_template_sections()
    forms = get_all_template_forms()
    return render_template("view_templates.html", sections=sections, forms=forms)
