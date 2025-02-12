from flask import url_for

from app.db.models.application_config import Form


def json_import(data, template_name, filename):
    from app.import_config.load_form_json import load_json_from_file

    return load_json_from_file(data, template_name, filename)


def build_form_rows(forms: list[dict]) -> list[dict]:
    rows = []
    for form in forms:
        row = [
            # TODO need a refactor to get rid of the html
            {
                "html": "<a class='govuk-link govuk-link--no-visited-state' "
                f"href='{url_for('template_bp.template_details', form_id=form.form_id)}'>{form.template_name}</a>"
            },
            {"classes": "govuk-!-width-one-third", "text": form.name_in_apply_json["en"]},
            {
                "classes": "govuk-!-text-align-right fab-nowrap",
                "html": "<a class='govuk-link govuk-link--no-visited-state' href='"
                f"{url_for('template_bp.edit_template', form_id=form.form_id, actions='template_table')}'>Edit details</a>",  # noqa: E501
            },
        ]
        rows.append(row)
    return rows
