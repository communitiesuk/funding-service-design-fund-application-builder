import json

from flask import current_app
from jsonschema import ValidationError

from app.db.queries.round import get_round_by_id
from app.export_config.helpers import write_config
from app.shared.json_validation import validate_form_json


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
    current_app.logger.info("Generating form JSONs for round {round_id}", extra=dict(round_id=round_id))
    for section in round.sections:
        for form in section.forms:
            result = form.form_json
            form_json = json.dumps(result, indent=4)
            try:
                validate_form_json(result)
                write_config(form_json, form.runner_publish_name, round.short_name, "form_json", base_output_dir)
            except ValidationError:
                current_app.logger.error(
                    "Form JSON for {runner_publish_name} is invalid.",
                    extra=dict(runner_publish_name=form.runner_publish_name),
                )
