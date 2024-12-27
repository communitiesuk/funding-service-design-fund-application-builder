from flask import url_for

from app.db.models.application_config import Form


def json_import(data, template_name, filename):
    from app.import_config.load_form_json import load_json_from_file

    load_json_from_file(data, template_name, filename)


def build_rows(forms: list[Form]) -> list[dict]:
    rows = []
    for form in forms:
        row = [
            {
                "html": "<a class='govuk-link--no-visited-state' "
                f"href='{url_for('index_bp.preview_form', form_id=form.form_id)}'>{form.template_name}</a>"
            },
            {"text": form.name_in_apply_json["en"]},
            {"text": form.runner_publish_name},
            {
                "html": "<a class='govuk-link--no-visited-state' href='"
                f"{url_for('template_bp.edit_template', form_id=form.form_id)}'>Edit</a> &nbsp;"
                "<a class='govuk-link--no-visited-state' href='"
                f"{url_for('template_bp.delete_template', form_id=form.form_id)}'>Delete</a>"
            },
        ]
        rows.append(row)
    return rows
