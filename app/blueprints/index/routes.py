import uuid

import requests
from flask import Blueprint, current_app, g, redirect, render_template, request, session, url_for
from fsd_utils.authentication.decorators import login_requested

from app.db.queries.application import get_form_by_id
from app.shared.form_store_api import FormNotFoundError, FormStoreAPIService
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
    Generates the form json for a chosen form, publishes it to the form runner,
    and returns a redirect to that form in preview mode.
    """
    api_service = FormStoreAPIService()
    form = get_form_by_id(form_id)
    published_form_response = api_service.get_published_form(form.url_path)
    if not published_form_response:
        raise FormNotFoundError(url_path=form.url_path)
    runner_form_id = form.url_path

    # Get the user's JWT token from their cookie
    user_token = request.cookies.get(Config.FSD_USER_TOKEN_COOKIE_NAME)

    # In development, we might not have a real token due to DEBUG_USER
    is_development = Config.FLASK_ENV == "development"

    if not user_token and not is_development:
        current_app.logger.error("No user token found for publish request")
        return "Authentication required", 401

    try:
        headers = {"Content-Type": "application/json"}

        # Only add auth cookie if we have a token (production/real auth)
        if user_token:
            headers["Cookie"] = f"{Config.FSD_USER_TOKEN_COOKIE_NAME}={user_token}"

        publish_response = requests.post(
            url=Config.FORM_RUNNER_PUBLISH_URL,
            json={"id": runner_form_id, "configuration": published_form_response.published_json},
            headers=headers,
            timeout=10,
        )

        if not str(publish_response.status_code).startswith("2"):
            current_app.logger.error("Publish failed: %s - %s", publish_response.status_code, publish_response.text)
            return f"Error during form publish: {publish_response.status_code}", 500

    except Exception as e:
        current_app.logger.error("Exception during publish: %s", e)
        return "Unable to publish form", 500

    # Now the form is in the cache, redirect to preview it
    preview_url = f"{Config.FORM_RUNNER_EXTERNAL_HOST}/{runner_form_id}?form_session_identifier=preview/{uuid.uuid4()}"
    return redirect(preview_url)


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


@index_bp.route("/accessibility_statement")
def accessibility_statement():
    return render_template("accessibility_statement.html")
