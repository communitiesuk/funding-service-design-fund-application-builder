from flask import url_for

from app.db.models import Fund


def build_fund_rows(funds: list[dict]) -> list[dict]:
    rows = []
    for fund in funds:
        row = [
            # TODO need a refactor to get rid of the html
            {
                "html": f"""<a class='govuk-link govuk-link--no-visited-state'
                href={url_for("fund_bp.view_fund_details", fund_id=fund.fund_id)}>{fund.name_json["en"]}</a>"""
            },
            {"classes": "govuk-!-width-one-half", "text": fund.description_json["en"]},
            {"text": fund.funding_type.get_text_for_display()},
        ]
        rows.append(row)
    return rows
