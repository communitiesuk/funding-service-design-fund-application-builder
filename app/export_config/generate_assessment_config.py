import copy
import json

from app.all_questions.metadata_utils import form_json_to_assessment_display_types
from app.db import db
from app.db.models import Form, Section
from app.db.models.application_config import READ_ONLY_COMPONENTS, ComponentType
from app.export_config import helpers
from app.shared.form_store_api import FormStoreAPIService
from app.shared.helpers import find_enum, human_to_kebab_case


def _get_component_type(component: dict) -> ComponentType:
    component_type = component.get("type")
    if component_type is None or (established_component_type := find_enum(ComponentType, component_type)) is None:
        raise ValueError(f"Component type not found: {component_type}")
    return established_component_type


def generate_assessment_config_for_round(fund_config, round_config, base_output_dir):
    # The following config is not tested for production use
    # It is generated to make local testing easier - you can add an application to fab and export it with a basic
    # auto-generated assessment config.
    # Each form is a sub-critiera, each page a theme. Half scored, half unscored.
    # The output in the assessment_store folder needs to be added to the
    # assessment_mapping_fund_round file in assessment-store
    api_service = FormStoreAPIService()
    fund_id = fund_config["id"]
    round_id = round_config["id"]
    fund_short_name = fund_config["short_name"]
    round_short_name = round_config["short_name"]
    fund_round = f"{str.upper(fund_short_name)}{str.upper(round_short_name)}"
    fund_round_ids = f"{fund_id}:{round_id}"

    unscored = []
    sections: list[Section] = (
        db.session.query(Section).filter(Section.round_id == round_id).order_by(Section.index).all()
    )
    for _i, section in enumerate(sections, start=1):
        criteria = {
            "id": human_to_kebab_case(section.name_in_apply_json["en"]),
            "name": section.name_in_apply_json["en"],
            "sub_criteria": [],
        }
        unscored.append(criteria)

        for form in section.forms:
            configuration = api_service.get_published_form(form.form_name)
            form: Form
            sc = {
                "id": form.form_name,
                "name": form.form_name,  # TODO: We should use some display name
                "themes": [],
            }
            for page in configuration.get("pages"):
                page: dict
                if page.get("path").lstrip("/") == "summary":
                    continue
                theme = {
                    "id": human_to_kebab_case(page.get("title")),
                    "name": page.get("title"),
                    "answers": [],
                }
                for component in page.get("components"):
                    component: dict
                    component_type = _get_component_type(component)
                    if component_type in READ_ONLY_COMPONENTS:
                        continue
                    answer = {
                        "field_id": component.get("name"),
                        "form_name": form.form_name,
                        "field_type": component_type.value[0].lower() + component_type.value[1:],
                        "presentation_type": form_json_to_assessment_display_types.get(component_type.name, "text"),
                        "question": component.get("title"),
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
