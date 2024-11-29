from flask import Blueprint
from flask import current_app
from flask import redirect
from flask import request
from flask import url_for
from fsd_utils.authentication.decorators import SupportedApp
from fsd_utils.authentication.decorators import check_internal_user
from fsd_utils.authentication.decorators import login_required

from app.blueprints.self_serve.data.data_access import clear_all_responses
from app.blueprints.self_serve.data.data_access import get_all_components
from app.blueprints.self_serve.data.data_access import get_all_pages
from app.blueprints.self_serve.data.data_access import get_all_sections
from app.blueprints.self_serve.data.data_access import get_responses
from app.blueprints.self_serve.data.data_access import get_saved_forms
from app.blueprints.self_serve.data.data_access import save_response

# Blueprint for dev related routes, eg. saving responses from when the form is in preview mode in the form runner
dev_bp = Blueprint(
    "dev_bp",
    __name__,
    url_prefix="/dev",
    template_folder="templates",
)


@dev_bp.route("/responses")
@login_required(return_app=SupportedApp.FUND_APPLICATION_BUILDER)
@check_internal_user
def view_responses():
    """
    Retrieves all responses received from a 'Save per page' callback when a form is in preview mode.
    These are saved in-memory, not the DB
    """
    responses = get_responses()
    return responses


@dev_bp.route("/responses/clear")
@login_required(return_app=SupportedApp.FUND_APPLICATION_BUILDER)
@check_internal_user
def clear_responses():
    """
    Clears all responses received from a 'Save per page' callback when a form is in preview mode.
    """
    clear_all_responses()
    return redirect(url_for("dev_bp.view_responses"))


@dev_bp.route("/save", methods=["PUT"])
@login_required(return_app=SupportedApp.FUND_APPLICATION_BUILDER)
@check_internal_user
def save_per_page():
    """
    Mock version of the 'save per page' route in application store - used to save and enable viewing of save
    per page requests for a form in preview mode to aid development/debugging
    """
    current_app.logger.info("Saving request")
    request_json = request.get_json(force=True)
    current_app.logger.info(request_json)
    form_dict = {
        "application_id": "",
        "form_name": request_json["name"],
        "question_json": request_json["questions"],
        "is_summary_page_submit": request_json["metadata"].get("isSummaryPageSubmit", False),
    }
    updated_form = save_response(form_dict=form_dict)
    return updated_form, 201


# ====================================================================================================
# Functions below this line are used by the original prototype version (drag and drop) before being
# updated to use the database
# ====================================================================================================


@dev_bp.route("/forms")
@login_required(return_app=SupportedApp.FUND_APPLICATION_BUILDER)
@check_internal_user
def view_forms():
    forms = get_saved_forms()
    return forms


@dev_bp.route("/pages")
@login_required(return_app=SupportedApp.FUND_APPLICATION_BUILDER)
@check_internal_user
def view_pages():
    forms = get_all_pages()
    return forms


@dev_bp.route("/sections")
@login_required(return_app=SupportedApp.FUND_APPLICATION_BUILDER)
@check_internal_user
def view_sections():
    forms = get_all_sections()
    return forms


@dev_bp.route("/questions")
@login_required(return_app=SupportedApp.FUND_APPLICATION_BUILDER)
@check_internal_user
def view_questions():
    forms = get_all_components()
    return forms
