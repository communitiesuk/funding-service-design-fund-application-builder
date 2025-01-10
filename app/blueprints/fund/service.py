from flask import url_for

from app.db.models import Fund


def build_fund_rows(funds: list[Fund]) -> list[dict]:
    rows = []
    for fund in funds:
        row = [
            {
                "html": f"""
                <a class='govuk-link--no-visited-state'
                href='{url_for('fund_bp.view_grant_details', grant_id=fund.fund_id)}'>
                {fund.name_json['en']}
                </a>
                """
            },
            {"text": fund.description_json["en"]},
            {"text": fund.funding_type.get_text_for_display()},
        ]
        rows.append(row)
    return rows
