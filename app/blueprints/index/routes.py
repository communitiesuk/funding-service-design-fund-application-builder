import json
import uuid
from random import randint

import requests
from flask import Blueprint, Response, g, redirect, render_template, session, url_for
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
            url=Config.FORM_RUNNER_PUBLISH_URL, json={"id": form_id, "configuration": form_json}
        )
        if not str(publish_response.status_code).startswith("2"):
            return "Error during form publish", 500
    except Exception as e:
        return f"unable to publish form: {str(e)}", 500
    return redirect(f"{Config.FORM_RUNNER_EXTERNAL_HOST}/{form_id}?form_session_identifier=preview/{uuid.uuid4()}")


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


@index_bp.route("/back")
def go_back():
    # If there are previous pages, pop the last one and redirect
    if len(session["visited_pages"]) > 1:
        history = session["visited_pages"]
        history.pop()  # Remove the current page
        prev_page = history[-1]
        session["visited_pages"] = history
        session.modified = True
        return redirect(url_for(prev_page["endpoint"], **prev_page["view_args"], **prev_page["query_params"]))
    else:
        return redirect(url_for("index_bp.index"))  # If no previous page, go home
