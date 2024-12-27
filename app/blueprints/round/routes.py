import json
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
from app.db.queries.fund import get_all_funds
from app.db.queries.round import get_round_by_id
from app.shared.helpers import all_funds_as_govuk_select_items, error_formatter

INDEX_BP_DASHBOARD = "index_bp.dashboard"

round_bp = Blueprint(
    "round_bp",
    __name__,
    url_prefix="/rounds",
    template_folder="templates",
)


@round_bp.route("/create", methods=["GET", "POST"])
@round_bp.route("/<round_id>", methods=["GET", "POST"])
def round(round_id=None):
    """
    Renders a template to select a fund and add or update a round to that fund. If saved, validates the round form data
    and saves to DB
    """
    form = RoundForm()
    all_funds = get_all_funds()
    params = {"all_funds": all_funds_as_govuk_select_items(all_funds)}
    params["selected_fund_id"] = request.form.get("fund_id", None)
    params["welsh_availability"] = json.dumps({str(fund.fund_id): fund.welsh_available for fund in all_funds})

    if round_id:
        existing_round = get_round_by_id(round_id)
        form = populate_form_with_round_data(existing_round, RoundForm)

    if form.validate_on_submit():
        if round_id:
            update_existing_round(existing_round, form)
            flash(f"Updated round {existing_round.title_json['en']}")
            return redirect(url_for("fund_bp.view_fund", fund_id=existing_round.fund_id))

        new_round = create_new_round(form)
        flash(f"Created round {new_round.title_json['en']}")
        return redirect(url_for(INDEX_BP_DASHBOARD))

    params["round_id"] = round_id
    params["form"] = form
    error = error_formatter(params["form"])

    return render_template("round.html", **params, error=error)


@round_bp.route("/<round_id>/clone")
def clone_round(round_id, fund_id):
    cloned = clone_single_round(
        round_id=round_id,
        new_fund_id=fund_id,
        new_short_name=f"R-C{randint(0, 999)}",  # NOSONAR
    )
    flash(f"Cloned new round: {cloned.short_name}")
    return redirect(url_for("fund_bp.view_fund", fund_id=fund_id))
