from datetime import datetime

from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)

from app.blueprints.fund.forms import FundForm
from app.blueprints.fund.services import build_fund_rows
from app.db.models.fund import Fund, FundingType
from app.db.queries.fund import add_fund, get_all_funds, get_fund_by_id, update_fund
from app.shared.helpers import flash_message
from app.shared.table_pagination import GovUKTableAndPagination

INDEX_BP_DASHBOARD = "index_bp.dashboard"
SELECT_GRANT_PAGE = "select_grant"
APPLICATIONS_DETAIL_PAGE = "view_application"
APPLICATION_EDIT_PAGE = "edit_application"
FUND_LIST_PAGE = "grants_table"
FUND_DETAILS_ROUTE = "fund_bp.view_fund_details"

# Blueprint for routes used by v1 of FAB - using the DB
fund_bp = Blueprint(
    "fund_bp",
    __name__,
    url_prefix="/grants",
    template_folder="templates",
)


@fund_bp.route("/", methods=["GET"])
def view_all_funds():
    """
    Renders list of grants in the grant page
    """
    params = GovUKTableAndPagination(
        table_header=[{"text": "Grant name"}, {"text": "Description"}, {"text": "Grant type"}],
        table_rows=build_fund_rows(get_all_funds()),
        current_page=int(request.args.get("page", 1)),
    ).__dict__
    return render_template("view_all_funds.html", **params)


@fund_bp.route("/<uuid:fund_id>", methods=["GET"])
def view_fund_details(fund_id):
    """
    Renders grant details page
    """
    form = FundForm()
    fund = get_fund_by_id(fund_id)
    return render_template("fund_details.html", form=form, fund=fund)


def _create_fund_get_previous_url(actions):
    if actions == FUND_LIST_PAGE:
        return url_for("fund_bp.view_all_funds")
    if actions == SELECT_GRANT_PAGE:
        return url_for("application_bp.select_fund")

    return url_for(INDEX_BP_DASHBOARD)


@fund_bp.route("/create", methods=["GET", "POST"])
def create_fund():
    """Creates a new fund"""
    form = FundForm()

    params = {"form": form, "fund_id": None}

    params["prev_nav_url"] = _create_fund_get_previous_url(request.args.get("actions"))

    if form.validate_on_submit():
        new_fund = Fund(
            name_json={"en": form.name_en.data, "cy": form.name_cy.data},
            title_json={"en": form.title_en.data, "cy": form.title_cy.data},
            description_json={"en": form.description_en.data, "cy": form.description_cy.data},
            welsh_available=form.welsh_available.data,
            short_name=form.short_name.data,
            audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
            funding_type=FundingType(form.funding_type.data),
            ggis_scheme_reference_number=(
                form.ggis_scheme_reference_number.data if form.ggis_scheme_reference_number.data else ""
            ),
        )

        add_fund(new_fund)
        if form.save_and_return_home.data:
            flash_message(
                message="New grant added successfully",
                href=url_for(FUND_DETAILS_ROUTE, fund_id=new_fund.fund_id),
                href_display_name=form.name_en.data,
                next_href=url_for("round_bp.create_round", fund_id=new_fund.fund_id),
                next_href_display_name="Set up a new application",
            )
            return redirect(url_for(INDEX_BP_DASHBOARD))

        flash_message(
            message="New grant added successfully",
            href=url_for(FUND_DETAILS_ROUTE, fund_id=new_fund.fund_id),
            href_display_name=form.name_en.data,
        )

        if request.args.get("actions") == "grants_table":
            return redirect(url_for("fund_bp.view_all_funds"))
        return redirect(url_for("round_bp.create_round", fund_id=new_fund.fund_id))

    return render_template("fund.html", **params)


def _edit_fund_get_previous_url(actions, fund_id, round_id):
    if actions == APPLICATIONS_DETAIL_PAGE:
        return url_for("round_bp.round_details", round_id=round_id)
    if actions == APPLICATION_EDIT_PAGE:
        return url_for("round_bp.edit_round", round_id=round_id)
    return url_for(FUND_DETAILS_ROUTE, fund_id=fund_id)


@fund_bp.route("/<uuid:fund_id>/edit", methods=["GET", "POST"])
def edit_fund(fund_id):
    """Updates an existing fund"""

    fund = get_fund_by_id(fund_id)
    round_id = request.args.get("round_id")

    params = {}
    prev_nav_url = _edit_fund_get_previous_url(request.args.get("actions"), fund_id, round_id)

    if request.method == "GET":
        form = FundForm(
            data={
                "fund_id": fund.fund_id,
                "name_en": fund.name_json.get("en", ""),
                "name_cy": fund.name_json.get("cy", ""),
                "title_en": fund.title_json.get("en", ""),
                "title_cy": fund.title_json.get("cy", ""),
                "short_name": fund.short_name,
                "description_en": fund.description_json.get("en", ""),
                "description_cy": fund.description_json.get("cy", ""),
                "welsh_available": "true" if fund.welsh_available else "false",
                "funding_type": fund.funding_type.value,
                "ggis_scheme_reference_number": (
                    fund.ggis_scheme_reference_number if fund.ggis_scheme_reference_number else ""
                ),
            }
        )
    else:
        form = FundForm()

    if form.validate_on_submit():
        fund.name_json["en"] = form.name_en.data
        fund.name_json["cy"] = form.name_cy.data
        fund.title_json["en"] = form.title_en.data
        fund.title_json["cy"] = form.title_cy.data
        fund.description_json["en"] = form.description_en.data
        fund.description_json["cy"] = form.description_cy.data
        fund.welsh_available = form.welsh_available.data
        fund.short_name = form.short_name.data
        fund.audit_info = {"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "update"}
        fund.funding_type = form.funding_type.data
        fund.ggis_scheme_reference_number = (
            form.ggis_scheme_reference_number.data if form.ggis_scheme_reference_number.data else ""
        )
        update_fund(fund)

        if form.save_and_return_home.data:
            flash_message(
                message="Grant updated",
                href=url_for(FUND_DETAILS_ROUTE, fund_id=fund.fund_id),
                href_display_name=form.name_en.data,
            )
            return redirect(url_for(INDEX_BP_DASHBOARD))
        flash_message(message="Grant updated")
        return redirect(prev_nav_url)

    params.update({"fund_id": fund_id, "form": form, "prev_nav_url": prev_nav_url})
    return render_template("fund.html", **params)
