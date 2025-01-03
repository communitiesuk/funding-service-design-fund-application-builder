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
    create_new_round,
    populate_form_with_round_data,
    update_existing_round,
)
from app.db.queries.clone import clone_single_round
from app.db.queries.fund import get_all_funds, get_fund_by_id
from app.db.queries.round import get_round_by_id
from app.shared.helpers import error_formatter

INDEX_BP_DASHBOARD = "index_bp.dashboard"

round_bp = Blueprint(
    "round_bp",
    __name__,
    url_prefix="/rounds",
    template_folder="templates",
)


@round_bp.route("/select-fund", methods=["GET", "POST"])  # NOSONAR
def select_fund():
    """
    Intermediary page to select a Fund before creating a Round.
    """
    if request.method == "POST":
        fund_id = request.form.get("fund_id")
        if not fund_id:
            raise ValueError("Fund ID is required to create a round")
        return redirect(url_for("round_bp.create_round", fund_id=fund_id))
    fund_dropdown_items = [{"value": "", "text": "Select a fund"}]
    for fund in get_all_funds():
        fund_dropdown_items.append(
            {"value": str(fund.fund_id), "text": fund.short_name + " - " + fund.title_json["en"]}
        )
    return render_template("select_fund.html", fund_dropdown_items=fund_dropdown_items)


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
        flash(f"Created round {new_round.title_json['en']}")
        return redirect(url_for(INDEX_BP_DASHBOARD))
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
