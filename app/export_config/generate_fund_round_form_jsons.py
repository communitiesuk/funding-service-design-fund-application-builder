import json

from flask import current_app

from app.db.queries.fund import get_fund_by_id
from app.db.queries.round import get_round_by_id
from app.export_config.generate_form import build_form_json
from app.export_config.helpers import validate_json, write_config

form_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "startPage": {"type": "string"},
        "sections": {"type": "array"},
        "pages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "title": {"type": "string"},
                    "options": {"type": "object"},
                    "section": {"type": "string"},
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "options": {
                                    "type": "object",
                                    "properties": {"hideTitle": {"type": "boolean"}, "classes": {"type": "string"}},
                                },
                                "type": {"type": "string"},
                                "title": {"type": ["string", "null"]},
                                "content": {"type": ["string", "null"]},
                                "hint": {"type": "string"},
                                "schema": {
                                    "type": "object",
                                },
                                "name": {"type": "string"},
                                "metadata": {
                                    "type": "object",
                                },
                                "children": {"type": "array"},
                            },
                        },
                    },
                },
                "required": ["path", "title", "components"],
            },
        },
        "lists": {"type": "array"},
        "conditions": {"type": "array"},
        "outputs": {
            "type": "array",
        },
        "skipSummary": {"type": "boolean"},
        # Add other top-level keys as needed
    },
    "required": [
        "startPage",
        "name",
        "pages",
        "lists",
        "conditions",
        "outputs",
        "skipSummary",
        "sections",
    ],
}


def generate_form_jsons_for_round(round_id, base_output_dir=None):
    """
    Generates JSON configurations for all forms associated with a given funding round.

    This function iterates through all sections of a specified funding round, and for each form
    within those sections, it generates a JSON configuration. These configurations are then written
    to files named after the forms, organized by the round's short name.

    Args:
        round_id (str): The unique identifier for the funding round.

    The generated files are named after the form names and are stored in a directory
    corresponding to the round's short name.
    """
    if not round_id:
        raise ValueError("Round ID is required to generate form JSONs.")
    round = get_round_by_id(round_id)
    fund = get_fund_by_id(round.fund_id)
    current_app.logger.info("Generating form JSONs for round {round_id}", extra=dict(round_id=round_id))
    for section in round.sections:
        for form in section.forms:
            result = build_form_json(form=form, fund_title=fund.title_json["en"])
            form_json = json.dumps(result, indent=4)
            valid_json = validate_json(result, form_schema)
            if valid_json:
                write_config(form_json, form.runner_publish_name, round.short_name, "form_json", base_output_dir)
            else:
                current_app.logger.error(
                    "Form JSON for {runner_publish_name} is invalid.",
                    extra=dict(runner_publish_name=form.runner_publish_name),
                )
