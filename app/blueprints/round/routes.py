from random import randint

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.blueprints.round.forms import RoundForm
from app.blueprints.round.services import (
    build_round_rows,
    create_new_round,
    populate_form_with_round_data,
    update_existing_round,
)
from app.db.queries.clone import clone_single_round
from app.db.queries.fund import get_all_funds, get_fund_by_id
from app.db.queries.round import get_all_rounds, get_round_by_id
from app.shared.forms import SelectFundForm
from app.shared.generic_table_page import GenericTablePage
from app.shared.helpers import error_formatter

INDEX_BP_DASHBOARD = "index_bp.dashboard"

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
    params = GenericTablePage(
        page_heading="Applications",
        page_description="View existing applications or create a new one.",
        detail_text="Creating a new grant application",
        detail_description="Follow the step-by-step instructions to create a new grant application.",
        button_text="Create new application",
        button_url=url_for("round_bp.select_fund", action="applications_table"),
        table_header=[{"text": "Application name"}, {"text": "Grant"}, {"text": ""}],
        table_rows=build_round_rows(get_all_rounds()),
        current_page=int(request.args.get("page", 1)),
    ).__dict__
    return render_template("view_all_rounds.html", **params)


@round_bp.route("/select-grant", methods=["GET", "POST"])  # NOSONAR
def select_fund():
    """
    Intermediary page to select a Fund before creating a Round.
    """
    form = SelectFundForm()
    choices = [("", "Select a grant")]
    for fund in get_all_funds():
        choices.append((str(fund.fund_id), fund.short_name + " - " + fund.title_json["en"]))
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
    back_link = (
        url_for("round_bp.view_all_rounds")
        if request.args.get("action") == "applications_table"
        else url_for("index_bp.dashboard")
    )
    return render_template("select_fund.html", form=form, error=error, select_items=select_items, back_link=back_link)


@round_bp.route("/create", methods=["GET", "POST"])
def create_round():
    """
    Create a new round for a chosen fund.
    Expects a ?fund_id=... in the query string, set by the select_fund route or other means.
    """
    form = RoundForm()
    fund_id = request.args.get("fund_id", None)
    if not fund_id:
        raise ValueError("Fund ID is required to create a round")
    fund = get_fund_by_id(fund_id)
    if form.validate_on_submit():
        new_round = create_new_round(form)
        flash(f"""
            <h3 class="govuk-notification-banner__heading">New application created successfully</h3>
            <p class="govuk-body">
                <a class="govuk-notification-banner__link" href="#">
                View {new_round.title_json["en"]}
                </a>
            </p>
        """)
        match request.args.get("action") or request.form.get("action"):
            case "return_home":
                return redirect(url_for(INDEX_BP_DASHBOARD))
            case "applications_table":
                return redirect(url_for("round_bp.view_all_rounds"))
            case _:
                return redirect(url_for("application_bp.build_application", round_id=new_round.round_id))
    params = {
        "form": form,
        "fund": fund,
        "round_id": None,  # Since we're creating a new round, there's no round ID yet
    }
    error = error_formatter(form)
    return render_template("round.html", **params, error=error)


@round_bp.route("/<round_id>", methods=["GET", "POST"])  # NOSONAR
def edit_round(round_id):
    """
    Edit an existing round.
    """
    existing_round = get_round_by_id(round_id)
    if not existing_round:
        raise ValueError(f"Round with ID {round_id} not found")
    form = RoundForm()
    if request.method == "GET":
        form = populate_form_with_round_data(existing_round, RoundForm)
    if form.validate_on_submit():
        update_existing_round(existing_round, form)
        flash(f"Updated round {existing_round.title_json['en']}")
        if request.form.get("action") == "return_home":
            return redirect(url_for(INDEX_BP_DASHBOARD))
        return redirect(url_for("fund_bp.view_fund", fund_id=existing_round.fund_id))
    params = {
        "form": form,
        "fund": get_fund_by_id(existing_round.fund_id),
        "round_id": round_id,
    }
    error = error_formatter(form)
    return render_template("round.html", **params, error=error)


@round_bp.route("/<round_id>/clone")
def clone_round(round_id, fund_id):
    """
    Clone an existing round.
    """
    cloned = clone_single_round(
        round_id=round_id,
        new_fund_id=fund_id,
        new_short_name=f"R-C{randint(0, 999)}",  # NOSONAR
    )
    flash(f"Cloned new round: {cloned.short_name}")
    return redirect(url_for("fund_bp.view_fund", fund_id=fund_id))
