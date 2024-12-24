import json
from random import randint

import requests
from flask import (
    Blueprint,
    Response,
    g,
    redirect,
    render_template,
    url_for,
)
from fsd_utils.authentication.decorators import login_requested

from app.db.queries.application import get_form_by_id
from app.export_config.generate_form import build_form_json
from config import Config

INDEX_BP_DASHBOARD = "index_bp.dashboard"

# Blueprint for routes used by v1 of FAB - using the DB
index_bp = Blueprint(
    "index_bp",
    __name__,
    url_prefix="/",
    template_folder="templates",
)


@index_bp.route("/")
@login_requested
def index():
    if not g.is_authenticated:
        return redirect(url_for("index_bp.login"))
    return redirect(url_for("index_bp.dashboard"))


@index_bp.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@index_bp.route("/dashboard", methods=["GET"])
def dashboard():
    return render_template("dashboard.html")


def all_funds_as_govuk_select_items(all_funds: list) -> list:
    """
    Reformats a list of funds into a list of display/value items that can be passed to a govUk select macro
    in the html
    """
    return [{"text": f"{f.short_name} - {f.name_json['en']}", "value": str(f.fund_id)} for f in all_funds]


@index_bp.route("/preview/<form_id>", methods=["GET"])
def preview_form(form_id):
    """
    Generates the form json for a chosen form, does not persist this, but publishes it to the form runner using the
    'runner_publish_name' of that form. Returns a redirect to that form in the form-runner
    """
    form = get_form_by_id(form_id)
    form_json = build_form_json(form)
    form_id = form.runner_publish_name

    try:
        publish_response = requests.post(
            url=f"{Config.FORM_RUNNER_URL}/publish", json={"id": form_id, "configuration": form_json}
        )
        if not str(publish_response.status_code).startswith("2"):
            return "Error during form publish", 500
    except Exception as e:
        return f"unable to publish form: {str(e)}", 500
    return redirect(f"{Config.FORM_RUNNER_URL_REDIRECT}/{form_id}")


@index_bp.route("/download/<form_id>", methods=["GET"])
def download_form_json(form_id):
    """
    Generates form json for the selected form and returns it as a file download
    """
    form = get_form_by_id(form_id)
    form_json = build_form_json(form)

    return Response(
        response=json.dumps(form_json),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename=form-{randint(0, 999)}.json"},  # nosec B311
    )
