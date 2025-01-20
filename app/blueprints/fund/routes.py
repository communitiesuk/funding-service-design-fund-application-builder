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
from app.shared.helpers import all_funds_as_govuk_select_items, flash_message
from app.shared.table_pagination import GovUKTableAndPagination

INDEX_BP_DASHBOARD = "index_bp.dashboard"

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
        table_header=[{"text": "Grant Name"}, {"text": "Description"}, {"text": "Grant Type"}],
        table_rows=build_fund_rows(get_all_funds()),
        current_page=int(request.args.get("page", 1)),
    ).__dict__
    return render_template("view_all_funds.html", **params)


@fund_bp.route("/view", methods=["GET", "POST"])
def view_fund():
    """
    Renders a template providing a drop down list of funds. If a fund is selected, renders its config info
    """
    params = {"all_funds": all_funds_as_govuk_select_items(get_all_funds())}
    fund = None
    if request.method == "POST":
        fund_id = request.form.get("fund_id")
    else:
        fund_id = request.args.get("fund_id")
    if fund_id:
        fund = get_fund_by_id(fund_id)
        params["fund"] = fund
        params["selected_fund_id"] = fund_id
    return render_template("fund_config.html", **params)


@fund_bp.route("/<uuid:fund_id>", methods=["GET"])
def view_fund_details(fund_id):
    """
    Renders grant details page
    """
    form = FundForm()
    fund = get_fund_by_id(fund_id)
    return render_template("fund_details.html", form=form, fund=fund)


@fund_bp.route("/create", methods=["GET", "POST"])
def create_fund():
    """Creates a new fund"""
    form = FundForm()

    if form.validate_on_submit():
        new_fund = Fund(
            name_json={"en": form.name_en.data},
            title_json={"en": form.title_en.data},
            description_json={"en": form.description_en.data},
            welsh_available=form.welsh_available.data == "true",
            short_name=form.short_name.data,
            audit_info={"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "create"},
            funding_type=FundingType(form.funding_type.data),
            ggis_scheme_reference_number=(
                form.ggis_scheme_reference_number.data if form.ggis_scheme_reference_number.data else ""
            ),
        )
        add_fund(new_fund)
        flash_message(
            message="New grant added successfully",
            href=url_for("fund_bp.view_fund_details", fund_id=new_fund.fund_id),
            href_display_name=form.name_en.data,
        )
        match request.args.get("action") or request.form.get("action"):
            case "return_home":
                return redirect(url_for(INDEX_BP_DASHBOARD))
            case "grants_table":
                return redirect(url_for("fund_bp.view_all_funds"))
            case _:
                return redirect(url_for("round_bp.create_round", fund_id=new_fund.fund_id))

    return render_template("fund.html", form=form, fund_id=None)


@fund_bp.route("/<uuid:fund_id>/edit", methods=["GET", "POST"])
def edit_fund(fund_id):
    """Updates an existing fund"""
    fund = get_fund_by_id(fund_id)

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
        fund.welsh_available = form.welsh_available.data == "true"
        fund.short_name = form.short_name.data
        fund.audit_info = {"user": "dummy_user", "timestamp": datetime.now().isoformat(), "action": "update"}
        fund.funding_type = form.funding_type.data
        fund.ggis_scheme_reference_number = (
            form.ggis_scheme_reference_number.data if form.ggis_scheme_reference_number.data else ""
        )
        update_fund(fund)
        if request.form.get("action") == "return_home":
            return redirect(url_for(INDEX_BP_DASHBOARD))
        return redirect(url_for("fund_bp.view_fund_details", fund_id=fund.fund_id))

    return render_template("fund.html", form=form, fund_id=fund_id)
