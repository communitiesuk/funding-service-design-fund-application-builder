import copy

from flask import current_app

from app.db import db
from app.db.models import Form, Section
from app.db.queries.fund import get_fund_by_id
from app.db.queries.round import get_round_by_id
from app.export_config.helpers import write_config
from app.shared.data_classes import FundExport, FundSectionForm, FundSectionSection, RoundExport
from app.shared.form_store_api import FormNotFoundError, FormStoreAPIService

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
    api_service = FormStoreAPIService()

    ordered_sections = []
    # get round
    round = get_round_by_id(round_id)
    round_base_path = (
        round.section_base_path
    )  # ROUND_BASE_PATHS.get(round.short_name, 0)  # so this works for dummy data
    application_base_path = f"{round_base_path}.1"
    "sort by Section.index"
    sections = db.session.query(Section).filter(Section.round_id == round_id).order_by(Section.index).all()
    current_app.logger.info("Generating application display config for round {round_id}", extra=dict(round_id=round_id))

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
            display_name = api_service.get_display_name_from_url_path(form.url_path)
            if not display_name:
                raise FormNotFoundError(url_path=form.url_path)
            name_in_apply_json = {"en": f"{section.index}.{form.section_index} {display_name}", "cy": ""}
            form_name_json = {
                "en": form.url_path,
                "cy": "",
            }
            ordered_sections.append(
                FundSectionForm(
                    section_name=name_in_apply_json,
                    form_name_json=form_name_json,
                    tree_path=f"{application_base_path}.{section.index}.{form.section_index}",
                ).as_dict()
            )
    return ordered_sections


def generate_fund_config(round_id):
    round = get_round_by_id(round_id)
    fund_id = round.fund_id
    fund = get_fund_by_id(fund_id)
    current_app.logger.info("Generating fund config for fund {fund_id}", extra=dict(fund_id=fund_id))

    fund_export = FundExport(
        id=str(fund.fund_id),
        name_json=fund.name_json,
        title_json=fund.title_json,
        short_name=fund.short_name,
        description_json=fund.description_json,
        welsh_available=fund.welsh_available,
        funding_type=fund.funding_type.value,
        ggis_scheme_reference_number=fund.ggis_scheme_reference_number,
    )
    return fund_export.as_dict()


def generate_round_config(round_id):
    round = get_round_by_id(round_id)
    current_app.logger.info("Generating round config for round {round_id}", extra=dict(round_id=round_id))

    round_export = RoundExport(
        id=str(round.round_id),
        fund_id=str(round.fund_id),
        title_json=round.title_json,
        short_name=round.short_name,
        opens=round.opens.isoformat(),
        deadline=round.deadline.isoformat(),
        assessment_start=round.assessment_start.isoformat(),
        assessment_deadline=round.assessment_deadline.isoformat(),
        reminder_date=round.reminder_date.isoformat(),
        prospectus=round.prospectus_link,
        privacy_notice=round.privacy_notice_link,
        contact_email=round.contact_email,
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
        eligibility_config=round.eligibility_config,
        send_deadline_reminder_emails=round.send_deadline_reminder_emails,
        send_incomplete_application_emails=round.send_incomplete_application_emails,
        eoi_decision_schema=round.eoi_decision_schema,
    )

    return round_export.as_dict()


def generate_config_for_round(round_id, base_output_dir=None, write_files=True):
    """
    Generates configuration for a specific funding round.

    This function orchestrates the generation of various configurations needed for a funding round.
    It calls three specific functions in sequence to generate the fund configuration, round configuration,
    and application display configuration for the given round ID.

    Args:
        round_id (str): The unique identifier for the funding round.
        base_output_dir (str, optional): Directory to write config files to.
        write_files (bool): Whether to write config files to disk. Defaults to True.

    Returns:
        tuple: (fund_config, round_config) or complete fund_round_export dict if write_files=False

    The functions called within this function are:
    - generate_fund_config: Generates the fund configuration for the given round ID.
    - generate_round_config: Generates the round configuration for the given round ID.
    - generate_application_display_config: Generates the application display configuration for the given round ID.
    """
    if round_id is None:
        raise ValueError("Valid round ID is required to generate configuration.")

    # Create fresh template each time to avoid caching issues
    fund_round_export = {"sections_config": [], "fund_config": {}, "round_config": [], "base_path": None}

    fund_config = generate_fund_config(round_id)
    fund_round_export["fund_config"] = fund_config
    round_config = generate_round_config(round_id)
    fund_round_export["round_config"] = round_config
    round_display_config = generate_application_display_config(round_id)
    fund_round_export["sections_config"] = round_display_config

    # Set base_path from round data
    round = get_round_by_id(round_id)
    fund_round_export["base_path"] = round.section_base_path

    if write_files:
        write_config(
            fund_round_export,
            fund_config["short_name"],
            fund_round_export["round_config"]["short_name"],
            "python_file",
            base_output_dir,
        )
        return fund_config, round_config
    else:
        # Return complete structure for API usage
        return fund_round_export
