from datetime import datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.blueprints.fund.forms import FundForm
from app.blueprints.fund_builder.routes import all_funds_as_govuk_select_items
from app.db.models.fund import Fund, FundingType
from app.db.queries.fund import add_fund, get_all_funds, get_fund_by_id, update_fund
from app.shared.helpers import error_formatter

BUILD_FUND_BP_DASHBOARD = "build_fund_bp.dashboard"

# Blueprint for routes used by v1 of FAB - using the DB
fund_bp = Blueprint(
    "fund_bp",
    __name__,
    url_prefix="/fund",
    template_folder="templates",
)


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
    params["breadcrumb_items"] = [
        {"text": "Home", "href": url_for(BUILD_FUND_BP_DASHBOARD)},
        {"text": fund.title_json["en"] if fund else "Manage Application Configuration", "href": "#"},
    ]

    return render_template("fund_config.html", **params)


@fund_bp.route("", methods=["GET", "POST"])
@fund_bp.route("/<fund_id>", methods=["GET", "POST"])
def fund(fund_id=None):
    """
    Renders a template to allow a user to add or update a fund, when saved validates the form data and saves to DB
    """
    if fund_id:
        fund = get_fund_by_id(fund_id)
        fund_data = {
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
        form = FundForm(data=fund_data)
    else:
        form = FundForm()

    if form.validate_on_submit():
        if fund_id:
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
            flash(f"Updated fund {form.title_en.data}")
            return redirect(url_for("fund_bp.view_fund", fund_id=fund.fund_id))

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
        flash(f"Created fund {form.name_en.data}")
        return redirect(url_for(BUILD_FUND_BP_DASHBOARD))

    error = error_formatter(form)
    return render_template("fund.html", form=form, fund_id=fund_id, error=error)
