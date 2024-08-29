import json

from flask import current_app

from app.db.queries.round import get_round_by_id
from app.export_config.generate_form import build_form_json
from app.export_config.helpers import validate_json
from app.export_config.helpers import write_config

form_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "metadata": {"type": "object"},
        "startPage": {"type": "string"},
        "backLinkText": {"type": "string"},
        "sections": {"type": "array"},
        "pages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "title": {"type": "string"},
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
                                "title": {"type": "string"},
                                "hint": {"type": "string"},
                                "schema": {"type": "object"},
                                "name": {"type": "string"},
                                "metadata": {
                                    "type": "object",
                                },
                            },
                        },
                    },
                },
                "required": ["path", "title", "components"],
            },
        },
        "lists": {"type": "array"},
        "conditions": {"type": "array"},
        "fees": {"type": "array"},
        "outputs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "title": {"type": "string"},
                    "type": {"type": "string"},
                    "outputConfiguration": {
                        "type": "object",
                        "properties": {"savePerPageUrl": {"type": "boolean"}},
                        "required": ["savePerPageUrl"],
                    },
                },
                "required": ["name", "title", "type", "outputConfiguration"],
            },
        },
        "skipSummary": {"type": "boolean"},
        # Add other top-level keys as needed
    },
    "required": [
        "metadata",
        "startPage",
        "backLinkText",
        "pages",
        "lists",
        "conditions",
        "fees",
        "outputs",
        "skipSummary",
        "name",
        "sections",
    ],
}


def generate_form_jsons_for_round(round_id):
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
    current_app.logger.info(f"Generating form JSONs for round {round_id}.")
    for section in round.sections:
        for form in section.forms:
            result = build_form_json(form)
            form_json = json.dumps(result, indent=4)
            valid_json = validate_json(result, form_schema)
            if valid_json:
                write_config(form_json, form.runner_publish_name, round.short_name, "form_json")
            else:
                current_app.logger.error(f"Form JSON for {form.runner_publish_name} is invalid.")
