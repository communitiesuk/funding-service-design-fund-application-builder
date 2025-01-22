from flask import render_template, url_for

from app.db.models.application_config import Form


def json_import(data, template_name, filename):
    from app.import_config.load_form_json import load_json_from_file

    return load_json_from_file(data, template_name, filename)


def build_rows(forms: list[Form]) -> list[dict]:
    rows = []
    for form in forms:
        row = [
            {
                "classes": "govuk-!-width-one-third",
                "html": render_template(
                    "partials/link.html",
                    url=url_for("template_bp.template_details", form_id=form.form_id),
                    text=f"Apply for {form.template_name}",
                ),
            },
            {"classes": "govuk-!-width-one-third", "text": form.name_in_apply_json["en"]},
            {
                "classes": "govuk-!-text-align-right govuk-!-width-one-quarter",
                "html": render_template(
                    "partials/link.html",
                    url=url_for("template_bp.edit_template", form_id=form.form_id),
                    text="Edit details",
                ),
            },
        ]
        rows.append(row)
    return rows
