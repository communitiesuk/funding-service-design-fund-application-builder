import json
import os

import click

from app.all_questions.metadata_utils import form_json_to_assessment_display_types
from app.db import db
from app.db.models import Component, Section
from app.db.models import Criteria
from app.db.models import Subcriteria
from app.db.models import Theme
from app.db.models.round import Round
from app.db.queries.application import get_form_for_component
from app.export_config import helpers
from app.export_config.generate_form import human_to_kebab_case


# # TODO this is copied from fund-store metadata_utils for now
# form_json_to_assessment_display_types = {
#     "numberfield": "integer",
#     "textfield": "text",
#     "yesnofield": "text",
#     "freetextfield": "free_text",
#     "checkboxesfield": "list",
#     "multiinputfield": "table",
#     "clientsidefileuploadfield": "s3bucketPath",
#     "radiosfield": "text",
#     "emailaddressfield": "text",
#     "telephonenumberfield": "text",
#     "ukaddressfield": "address",
# }


def generate_field_info_from_forms(forms_dir: str) -> dict:
    """Generates the display info for all fields in a form

    Args:
        forms_dir (str): Directory containing the forms

    Returns:
        dict: Dictionary of field IDs to display info
    """
    results = {}
    for file_name in os.listdir(forms_dir):
        with open(os.path.join(forms_dir, file_name), "r") as f:
            form_data = json.load(f)
            results.update(build_answers_from_form(form_data, file_name.split(".")[0]))

    return results


def build_answers_from_form(form_data: dict, form_name: str) -> dict:
    """Generates the list of display info for a particular form

    Args:
        form_data (dict): Full form data
        form_name (str): name of this form

    Returns:
        dict: Dictionary of field IDs to display info
    """
    results = {}
    for page in form_data["pages"]:
        for component in page["components"]:
            question = component.get("title", None)
            if component["type"].lower() == "multiinputfield":
                question = [page["title"]]
                child_fields = {}
                for field in component["children"]:
                    child_fields[field["name"]] = {
                        "column_title": field["title"],
                        "type": field["type"],
                    }
                question.append(child_fields)

            results[component["name"]] = {
                "field_id": component["name"],
                "form_name": form_name,
                "field_type": component["type"],
                # TODO fix this "presentation_type":
                # form_json_to_assessment_display_types.get(component["type"].lower(), None),
                "question": question,
            }

    return results


def build_answer(component: Component) -> dict:
    form = get_form_for_component(component)
    return {
        "field_id": component.component_id,
        "form_name": form.runner_publish_name,
        "field_type": component.type,
        "presentation_type": component.assessment_display_type,
        "question": component.title,
    }


def build_theme(theme: Theme) -> dict:
    """Creates a theme object and populates with the display info for the answers in that theme

    Args:
        theme_id (str): ID of the theme
        field_info (dict): Dictionary of field display info for all fields

    Returns:
        dict: Dictionary representing a theme within the assessment config
    """
    built_theme = {"id": theme.theme_id, "name": theme.name, "answers": []}
    for component in theme.components:
        built_theme["answers"].append(build_answer(component))

    return built_theme


def build_subcriteria(sc: Subcriteria) -> dict:
    """Generates a sub criteria, containing themes

    Args:
        sub_criteria (dict): Input subcriteria details
        field_info (dict): Dictionary of fields and their display info

    Returns:
        dict: Dictionary of subcriteria IDs to their config (containing themes)
    """
    built_sc = {"id": sc.subcriteria_id, "name": sc.name, "themes": []}
    for theme in sc.themes:
        built_sc["themes"].append(build_theme(theme))
    return built_sc


def build_assessment_config(criteria_list: list[Criteria]) -> dict:
    """Builds a dictionary represting the full assessment config based on the input data

    Args:
        input_data (dict): Dictionary of input data (eg. test_data/in/ns_unscored.json)
        field_info (dict): Dictionary of field IDs to their display info

    Returns:
        dict: Full assessment display config
    """
    results = {}
    unscored_sections = []
    scored_sections = []
    for criteria in criteria_list:
        built_criteria = {
            "id": criteria.criteria_id,
            "name": criteria.name,
            "subcriteria": [],
            "weighting": criteria.weighting,
        }
        for sc in criteria.subcriteria:
            built_criteria["subcriteria"].append(build_subcriteria(sc=sc))

        if criteria.weighting > 0:
            scored_sections.append(built_criteria)
        else:
            unscored_sections.append(built_criteria)

    results["unscored_sections"] = unscored_sections
    results["scored_sections"] = scored_sections
    return results


@click.command()
@click.option(
    "--input_folder",
    default="./config_reuse/test_data/in/",
    help="Input configuration",
    prompt=True,
)
@click.option(
    "--input_file",
    default="assmnt_unscored.json",
    help="Input configuration",
    prompt=True,
)
@click.option(
    "--output_folder",
    default="./config_reuse/test_data/out",
    help="Output destination",
    prompt=True,
)
@click.option(
    "--output_file",
    default="assessment_mapping_unscored.json",
    help="Output destination",
    prompt=True,
)
@click.option(
    "--forms_dir",
    default="./config_reuse/test_data/out/forms/",
    help="Directory containing forms",
    prompt=True,
)
def generate_assessment_config(
    input_folder,
    input_file,
    output_folder,
    output_file,
    forms_dir,
):
    with open(os.path.join(input_folder, input_file), "r") as f:
        input_data = json.load(f)

    field_info = generate_field_info_from_forms(forms_dir)

    assessment_config = build_assessment_config(input_data, field_info)

    with open(os.path.join(output_folder, output_file), "w") as f:
        json.dump(assessment_config, f)


def generate_assessment_config_for_round(round_config, base_output_dir):
    round_id = round_config["id"]
    round = db.session.query(Round).filter(Round.round_id == round_id).one_or_none()

    unscored_criteria = ["unscored", "declarations"]
    unscored = []
    scored = []
    for criteria in round.criteria:
        criteria_slug_name = human_to_kebab_case(criteria.name)
        is_unscored = criteria_slug_name in unscored_criteria

        export_subcrieria = []
        for subcriteria in criteria.subcriteria:
            export_theme = []
            for theme in subcriteria.themes:
                answers = []
                for component in theme.components:
                    answers.append(
                        {
                            "field_id": component.runner_component_name,
                            "form_name": component.page.form.runner_publish_name,
                            "field_type": component.type.value[0].lower() + component.type.value[1:],
                            "presentation_type": form_json_to_assessment_display_types.get(component.type.name, "text"),
                            "question": component.title,
                        }
                    )

                export_theme.append(
                    {
                        "id": human_to_kebab_case(theme.name),
                        "name": theme.name,
                        "answers": answers,
                    }
                )

            export_subcrieria.append(
                {
                    "id": human_to_kebab_case(subcriteria.name),
                    "name": subcriteria.name,
                    "themes": export_theme,
                }
            )

        export_crieria = {
            "id": criteria_slug_name,
            "name": criteria.name,
            "sub_criteria": export_subcrieria,
        }

        if is_unscored:
            unscored.append(export_crieria)
        else:
            scored.append(export_crieria)

    helpers.write_config(unscored, "unscored", round.short_name, "assessment", base_output_dir)
    helpers.write_config(scored, "scored", round.short_name, "assessment", base_output_dir)


if __name__ == "__main__":
    generate_assessment_config()
