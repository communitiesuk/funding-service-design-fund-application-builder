from flask import render_template, url_for

from app.db.models import Fund


def build_fund_rows(funds: list[Fund]) -> list[dict]:
    rows = []
    for fund in funds:
        row = [
            {
                "classes": "govuk-!-width-one-third",
                "html": render_template(
                    "partials/link.html",
                    url=url_for("fund_bp.view_fund_details", fund_id=fund.fund_id),
                    text=fund.name_json["en"],
                ),
            },
            {"classes": "govuk-!-width-one-half", "text": fund.description_json["en"]},
            {"classes": "govuk-!-width-one-quarter", "text": fund.funding_type.get_text_for_display()},
        ]
        rows.append(row)
    return rows
