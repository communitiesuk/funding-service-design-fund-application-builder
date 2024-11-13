import copy
import json

from flask import current_app

from app.all_questions.metadata_utils import form_json_to_assessment_display_types
from app.db import db
from app.db.models import Form
from app.db.models import Section
from app.db.models.application_config import READ_ONLY_COMPONENTS
from app.db.queries.fund import get_fund_by_id
from app.db.queries.round import get_round_by_id
from app.export_config import helpers
from app.export_config.generate_form import human_to_kebab_case
from app.export_config.helpers import write_config
from app.shared.data_classes import FundExport
from app.shared.data_classes import FundSectionForm
from app.shared.data_classes import FundSectionSection
from app.shared.data_classes import RoundExport
from config import Config

# TODO : The Round path might be better as a placeholder to avoid conflict in the actual fund store.
# Decide on this further down the line.
ROUND_BASE_PATHS = {
    # Should increment for each new round, anything that shares the same base path will also share
    # the child tree path config.
    "TEST": 0,
    "COF_R2_W2": 1,
    "COF_R2_W3": 1,
    "COF_R3_W1": 2,
    "COF_R3_W2H": 4,
    "CYP_R1": 5,
    "DPI_R2": 6,
    "COF_R3_W3": 7,
    "COF_EOI": 8,
    "COF_R4_W1": 9,
    "HSRA": 10,
    "COF_R4_W2": 11,
}

TEMPLATE_FUND_ROUND_EXPORT = {"sections_config": [], "fund_config": {}, "round_config": [], "base_path": None}


def generate_application_display_config(round_id):

    ordered_sections = []
    # get round
    round = get_round_by_id(round_id)
    round_base_path = (
        round.section_base_path
    )  # ROUND_BASE_PATHS.get(round.short_name, 0)  # so this works for dummy data
    application_base_path = f"{round_base_path}.1"
    TEMPLATE_FUND_ROUND_EXPORT["base_path"] = round_base_path
    "sort by Section.index"
    sections = db.session.query(Section).filter(Section.round_id == round_id).order_by(Section.index).all()
    current_app.logger.info(f"Generating application display config for round {round_id}")

    for original_section in sections:
        section = copy.deepcopy(original_section)
        # add to ordered_sections list in order of index
        section.name_in_apply_json["en"] = f"{section.index}. {section.name_in_apply_json['en']}"
        section.name_in_apply_json["cy"] = (
            f"{section.index}. {section.name_in_apply_json['cy']}" if section.name_in_apply_json.get("cy") else ""
        )
        ordered_sections.append(
            FundSectionSection(
                section_name=section.name_in_apply_json, tree_path=f"{application_base_path}.{section.index}"
            ).as_dict()
        )
        forms = db.session.query(Form).filter(Form.section_id == section.section_id).order_by(Form.section_index).all()
        for original_form in forms:
            # Create a deep copy of the form object
            form = copy.deepcopy(original_form)
            form.name_in_apply_json["en"] = f"{section.index}.{form.section_index} {form.name_in_apply_json['en']}"
            form.name_in_apply_json["cy"] = (
                f"{section.index}.{form.section_index} {form.name_in_apply_json['cy']}"
                if form.name_in_apply_json.get("cy")
                else ""
            )
            form.runner_publish_name = {
                "en": form.runner_publish_name,
                "cy": "",
            }
            ordered_sections.append(
                FundSectionForm(
                    section_name=form.name_in_apply_json,
                    form_name_json=form.runner_publish_name,
                    tree_path=f"{application_base_path}.{section.index}.{form.section_index}",
                ).as_dict()
            )
    return ordered_sections


def generate_fund_config(round_id):
    round = get_round_by_id(round_id)
    fund_id = round.fund_id
    fund = get_fund_by_id(fund_id)
    current_app.logger.info(f"Generating fund config for fund {fund_id}")

    fund_export = FundExport(
        id=str(fund.fund_id),
        name_json=fund.name_json,
        title_json=fund.title_json,
        short_name=fund.short_name,
        description_json=fund.description_json,
        welsh_available=fund.welsh_available,
        owner_organisation_name="None",
        owner_organisation_shortname="None",
        owner_organisation_logo_uri="None",
        funding_type=fund.funding_type.value,
        ggis_scheme_reference_number=fund.ggis_scheme_reference_number,
    )
    return fund_export.as_dict()


def generate_round_config(round_id):
    round = get_round_by_id(round_id)
    current_app.logger.info(f"Generating round config for round {round_id}")

    round_export = RoundExport(
        id=str(round.round_id),
        fund_id=str(round.fund_id),
        title_json=round.title_json,
        short_name=round.short_name,
        opens=round.opens.isoformat(),
        deadline=round.deadline.isoformat(),
        assessment_start=round.assessment_start.isoformat(),
        assessment_deadline=round.assessment_deadline.isoformat(),
        application_reminder_sent=False,
        reminder_date=round.reminder_date.isoformat(),
        prospectus=round.prospectus_link,
        privacy_notice=round.privacy_notice_link,
        contact_us_banner_json=round.contact_us_banner_json,
        reference_contact_page_over_email=round.reference_contact_page_over_email,
        contact_email=round.contact_email,
        contact_phone=round.contact_phone,
        contact_textphone=round.contact_textphone,
        support_times=round.support_times,
        support_days=round.support_days,
        instructions_json=round.instructions_json,
        feedback_link=round.feedback_link,
        project_name_field_id=round.project_name_field_id,
        application_guidance_json=round.application_guidance_json,
        guidance_url=round.guidance_url,
        all_uploaded_documents_section_available=round.all_uploaded_documents_section_available,
        application_fields_download_available=round.application_fields_download_available,
        display_logo_on_pdf_exports=round.display_logo_on_pdf_exports,
        mark_as_complete_enabled=round.mark_as_complete_enabled,
        is_expression_of_interest=round.is_expression_of_interest,
        feedback_survey_config=round.feedback_survey_config,
        eoi_decision_schema=round.eoi_decision_schema,
    )

    return round_export.as_dict()


def generate_config_for_round(round_id):
    """
    Generates configuration for a specific funding round.

    This function orchestrates the generation of various configurations needed for a funding round.
    It calls three specific functions in sequence to generate the fund configuration, round configuration,
    and application display configuration for the given round ID.

    Args:
        round_id (str): The unique identifier for the funding round.

    The functions called within this function are:
    - generate_fund_config: Generates the fund configuration for the given round ID.
    - generate_round_config: Generates the round configuration for the given round ID.
    - generate_application_display_config: Generates the application display configuration for the given round ID.
    """
    if round_id is None:
        raise ValueError("Valid round ID is required to generate configuration.")
    fund_config = generate_fund_config(round_id)
    TEMPLATE_FUND_ROUND_EXPORT["fund_config"] = fund_config
    round_config = generate_round_config(round_id)
    TEMPLATE_FUND_ROUND_EXPORT["round_config"] = round_config
    round_display_config = generate_application_display_config(round_id)
    TEMPLATE_FUND_ROUND_EXPORT["sections_config"] = round_display_config
    fund_round_export = TEMPLATE_FUND_ROUND_EXPORT
    write_config(
        fund_round_export, fund_config["short_name"], fund_round_export["round_config"]["short_name"], "python_file"
    )

    if Config.GENERATE_LOCAL_CONFIG:
        generate_default_assessment_mappings(fund_config, round_config)


def generate_default_assessment_mappings(fund_config, round_config):
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

    scored = []
    unscored = []
    sections = db.session.query(Section).filter(Section.round_id == round_id).order_by(Section.index).all()
    for i, section in enumerate(sections, start=1):
        type_of_criteria = "scored" if i % 2 == 0 else "unscored"  # do a random half scored and unscored
        criteria = {
            "id": human_to_kebab_case(section.name_in_apply_json["en"]),
            "name": section.name_in_apply_json["en"],
            "sub_criteria": [],
        }
        if type_of_criteria == "scored":
            # half the sections will be scored, divide the weighting between them
            criteria["weighting"] = 1 / (len(sections) / 2)
            scored.append(criteria)
        else:
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
                    "id": human_to_kebab_case(page.name_in_apply_json["en"]),
                    "name": page.name_in_apply_json["en"],
                    "answers": [],
                }
                for component in page.components:
                    if component.type in READ_ONLY_COMPONENTS:
                        continue
                    answer = {
                        "field_id": component.runner_component_name,
                        "form_name": form.runner_publish_name,
                        "field_type": component.type.name,
                        "presentation_type": form_json_to_assessment_display_types.get(component.type.name, "text"),
                        "question": component.title,
                    }
                    theme["answers"].append(answer)
                sc["themes"].append(theme)
            criteria["sub_criteria"].append(sc)
    temp_assess_output = copy.deepcopy(helpers.temp_assess_output)
    temp_assess_output = temp_assess_output.substitute(
        fund_round=fund_round,
        fund_id=fund_id,
        round_id=round_id,
        fund_round_ids=fund_round_ids,
        fund_short_name=fund_short_name,
        scored=json.dumps(scored),
        unscored=json.dumps(unscored),
    )
    write_config(temp_assess_output, "temp_assess", round_short_name, "temp_assess")
