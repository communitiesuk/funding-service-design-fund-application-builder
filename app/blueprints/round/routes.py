from random import randint

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.blueprints.fund.forms import FundForm
from app.blueprints.round.forms import CloneRoundForm, RoundForm
from app.blueprints.round.services import (
    build_round_rows,
    create_new_round,
    populate_form_with_round_data,
    update_existing_round,
)
from app.db.queries.clone import clone_single_round
from app.db.queries.fund import get_all_funds, get_fund_by_id
from app.db.queries.round import get_all_rounds, get_round_by_id, delete_selected_round
from app.shared.forms import SelectFundForm
from app.shared.helpers import flash_message
from app.shared.table_pagination import GovUKTableAndPagination
from config import Config

INDEX_BP_DASHBOARD = "index_bp.dashboard"
ROUND_DETAILS = "round_bp.round_details"
BUILD_APPLICATION = "application_bp.build_application"
ROUND_LIST = "round_bp.view_all_rounds"

round_bp = Blueprint(
    "round_bp",
    __name__,
    url_prefix="/rounds",
    template_folder="templates",
)


@round_bp.route("/", methods=["GET"])
def view_all_rounds():
    """
    Renders a list of rounds in the application page
    """
    params = GovUKTableAndPagination(
        table_header=[{"text": "Application name"}, {"text": "Grant"}, {"text": "Round"}, {"text": ""}],
        table_rows=build_round_rows(get_all_rounds()),
        current_page=int(request.args.get("page", 1)),
    ).__dict__
    return render_template("view_all_rounds.html", **params)


@round_bp.route("/select-grant", methods=["GET", "POST"])
def select_fund():
    """
    Intermediary page to select a Fund before creating a Round.
    """
    form = SelectFundForm()
    choices = [("", "Select a grant")]
    for fund in get_all_funds():
        choices.append((str(fund.fund_id), fund.short_name + " - " + fund.name_json["en"]))
    form.fund_id.choices = choices
    if form.validate_on_submit():
        return redirect(
            url_for(
                "round_bp.create_round",
                fund_id=form.fund_id.data,
                **({"action": request.args.get("action")} if request.args.get("action") else {}),
            )
        )
    error = None
    if form.fund_id.errors:
        error = {"titleText": "There is a problem", "errorList": [{"text": form.fund_id.errors[0], "href": "#fund_id"}]}
    select_items = [{"value": value, "text": text} for value, text in choices]
    return render_template("select_fund.html", form=form, error=error, select_items=select_items)


def _create_round_get_previous_url(action):
    cancel_url = url_for(INDEX_BP_DASHBOARD)
    if action == "applications_table":
        cancel_url = url_for(ROUND_LIST)

    return cancel_url


@round_bp.route("/create", methods=["GET", "POST"])
def create_round():
    """
    Create a new round for a chosen fund.
    Expects a ?fund_id=... in the query string, set by the select_fund route or other means.
    """
    fund_id = request.args.get("fund_id", None)
    fund_form = FundForm()
    if not fund_id:
        raise ValueError("Fund ID is required to create a round")
    fund = get_fund_by_id(fund_id)
    form = RoundForm(data={"fund_id": fund_id, "welsh_available": fund.welsh_available})

    cancel_url = _create_round_get_previous_url(action=request.args.get("action"))

    if form.validate_on_submit():
        new_round = create_new_round(form)
        if form.save_and_return_home.data:
            flash_message(
                message="New application created",
                href=url_for(ROUND_DETAILS, round_id=new_round.round_id),
                href_display_name=fund.title_json["en"],
                next_href=url_for(BUILD_APPLICATION, round_id=new_round.round_id),
                next_href_display_name="Design your application",
            )
            return redirect(url_for(INDEX_BP_DASHBOARD))

        flash_message(
            message="New application created",
            href=url_for(ROUND_DETAILS, round_id=new_round.round_id),
            href_display_name=fund.title_json["en"],
        )

        if request.args.get("action") == "applications_table":
            return redirect(url_for(ROUND_LIST))
        return redirect(url_for(BUILD_APPLICATION, round_id=new_round.round_id))

    params = {
        "form": form,
        "fund": fund,
        "fund_form": fund_form,
        "cancel_url": cancel_url,
        "round_id": None,  # Since we're creating a new round, there's no round ID yet
    }
    return render_template("round.html", **params)


@round_bp.route("/<round_id>/edit", methods=["GET", "POST"])
def edit_round(round_id):
    """
    Edit an existing round.
    """
    existing_round = get_round_by_id(round_id)
    if not existing_round:
        raise ValueError(f"Round with ID {round_id} not found")

    fund = get_fund_by_id(existing_round.fund_id)
    form = RoundForm(data={"fund_id": existing_round.fund_id, "welsh_available": fund.welsh_available})
    fund_form = FundForm()
    if request.method == "GET":
        form = populate_form_with_round_data(existing_round, RoundForm)
    if form.validate_on_submit():
        update_existing_round(existing_round, form)
        if form.save_and_return_home.data:
            flash_message(
                message="Application updated",
                href=url_for(ROUND_DETAILS, round_id=existing_round.round_id),
                href_display_name=fund.title_json["en"],
                next_href=url_for(BUILD_APPLICATION, round_id=existing_round.round_id),
                next_href_display_name="Design your application",
            )
            return redirect(url_for(INDEX_BP_DASHBOARD))
        flash_message(message="Application updated")
        return redirect(url_for(ROUND_DETAILS, round_id=existing_round.round_id))

    prev_nav_url = url_for(ROUND_DETAILS, round_id=existing_round.round_id)
    params = {
        "form": form,
        "fund": fund,
        "fund_form": fund_form,
        "round_id": round_id,
        "cancel_url": prev_nav_url,
    }
    return render_template("round.html", **params)


@round_bp.route("/<round_id>/clone", methods=["POST"])
def clone_round(round_id):
    """
    Clone an existing round.
    """
    form = CloneRoundForm()
    msg = "Error copying application"
    if form.validate_on_submit():
        cloned = clone_single_round(
            round_id=round_id,
            new_fund_id=form.fund_id.data,
            new_short_name=f"R-C{randint(0, 999)}",
        )
        round_id = cloned.round_id
        msg = "Application copied"
    flash(msg)
    return redirect(url_for(ROUND_DETAILS, round_id=round_id))


@round_bp.route("/<round_id>")
def round_details(round_id):
    fund_round = get_round_by_id(round_id)
    form = RoundForm(data={"fund_id": fund_round.fund_id})
    cloned_form = CloneRoundForm(data={"fund_id": fund_round.fund_id})
    fund_form = FundForm()
    return render_template(
        "round_details.html", form=form, fund_form=fund_form, round=fund_round,
        cloned_form=cloned_form,
        feature_flags=Config.FEATURE_FLAGS
    )


@round_bp.route("/<uuid:round_id>/delete", methods=["GET"])
def delete_round(round_id):
    if not Config.FEATURE_FLAGS.get('feature_delete'):
        return "Delete Feature Disabled", 403
    delete_selected_round(round_id)
    return redirect(url_for("round_bp.view_all_rounds"))
