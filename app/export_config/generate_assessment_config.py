import copy
import json
import os

import click

from app.all_questions.metadata_utils import form_json_to_assessment_display_types
from app.db import db
from app.db.models import Component, Criteria, Section, Subcriteria, Theme
from app.db.models.application_config import READ_ONLY_COMPONENTS
from app.db.queries.application import get_form_for_component
from app.export_config import helpers


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


def generate_assessment_config_for_round(fund_config, round_config, base_output_dir):
    # The following config is not tested for production use
    # It is generated to make local testing easier - you can add an application to fab and export it with a basic
    # auto-generated assessment config.
    # Each form is a sub-critiera, each page a theme. Half scored, half unscored.
    # The output in the assessment_store folder needs to be added to the
    # assessment_mapping_fund_round file in assessment-store
    fund_id = fund_config["id"]
    round_id = round_config["id"]
    fund_short_name = fund_config["short_name"]
    round_short_name = round_config["short_name"]
    fund_round = f"{str.upper(fund_short_name)}{str.upper(round_short_name)}"
    fund_round_ids = f"{fund_id}:{round_id}"

    unscored = []
    sections = db.session.query(Section).filter(Section.round_id == round_id).order_by(Section.index).all()
    for i, section in enumerate(sections, start=1):
        criteria = {
            "id": helpers.human_to_kebab_case(section.name_in_apply_json["en"]),
            "name": section.name_in_apply_json["en"],
            "sub_criteria": [],
        }
        unscored.append(criteria)

        for form in section.forms:
            sc = {
                "id": form.runner_publish_name,
                "name": form.name_in_apply_json["en"],
                "themes": [],
            }
            for page in form.pages:
                if page.display_path == "summary":
                    continue
                theme = {
                    "id": helpers.human_to_kebab_case(page.name_in_apply_json["en"]),
                    "name": page.name_in_apply_json["en"],
                    "answers": [],
                }
                for component in page.components:
                    if component.type in READ_ONLY_COMPONENTS:
                        continue
                    answer = {
                        "field_id": component.runner_component_name,
                        "form_name": form.runner_publish_name,
                        "field_type": component.type.value[0].lower() + component.type.value[1:],
                        "presentation_type": form_json_to_assessment_display_types.get(component.type.name, "text"),
                        "question": component.title,
                    }
                    theme["answers"].append(answer)
                sc["themes"].append(theme)
            criteria["sub_criteria"].append(sc)
    assess_output = copy.deepcopy(helpers.assess_output)
    assess_output = assess_output.substitute(
        fund_round=fund_round,
        fund_id=fund_id,
        round_id=round_id,
        fund_round_ids=fund_round_ids,
        fund_short_name=fund_short_name,
        unscored=json.dumps(unscored),
    )
    helpers.write_config(assess_output, "assessment_config", round_short_name, "assessment", base_output_dir)


if __name__ == "__main__":
    generate_assessment_config()
