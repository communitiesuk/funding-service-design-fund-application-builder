import copy
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Optional

from flask import current_app

from app.config_generator.scripts.helpers import write_config
from app.db import db
from app.db.models import Form
from app.db.models import Section
from app.db.queries.fund import get_fund_by_id
from app.db.queries.round import get_round_by_id

# TODO : The Round path might be better as a placeholder to avoid conflict in the actual fund store.
# Decide on this further down the line.
ROUND_BASE_PATHS = {
    # Should increment for each new round, anything that shares the same base path will also share
    # the child tree path config.
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
    "R605": 12,
}


@dataclass
class SectionName:
    en: str
    cy: str


@dataclass
class FormNameJson:
    en: str
    cy: str


@dataclass
class FundSectionBase:
    section_name: SectionName
    tree_path: str


@dataclass
class FundSectionSection(FundSectionBase):
    requires_feedback: Optional[bool] = None


@dataclass
class FundSectionForm(FundSectionBase):
    form_name_json: FormNameJson


def generate_application_display_config(round_id):

    ordered_sections = []
    # get round
    round = get_round_by_id(round_id)
    round_base_path = ROUND_BASE_PATHS[round.short_name]
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
            FundSectionSection(section_name=section.name_in_apply_json, tree_path=f"{round_base_path}.{section.index}")
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
                    tree_path=f"{round_base_path}.{section.index}.{form.section_index}",
                )
            )
    write_config(ordered_sections, "sections_config", round.short_name, "python_file")


@dataclass
class NameJson:
    en: str
    cy: str


@dataclass
class TitleJson:
    en: str
    cy: str


@dataclass
class DescriptionJson:
    en: str
    cy: str


@dataclass
class ContactUsBannerJson:
    en: str = ""
    cy: str = ""


@dataclass
class FeedbackSurveyConfig:
    has_feedback_survey: Optional[bool] = None
    has_section_feedback: Optional[bool] = None
    is_feedback_survey_optional: Optional[bool] = None
    is_section_feedback_optional: Optional[bool] = None


@dataclass
class EligibilityConfig:
    has_eligibility: Optional[bool] = None


@dataclass
class FundExport:
    id: str
    short_name: dict
    welsh_available: bool
    owner_organisation_name: str
    owner_organisation_shortname: str
    owner_organisation_logo_uri: str
    name_json: NameJson = field(default_factory=NameJson)
    title_json: TitleJson = field(default_factory=TitleJson)
    description_json: DescriptionJson = field(default_factory=DescriptionJson)


@dataclass
class RoundExport:
    id: Optional[str] = None
    fund_id: Optional[str] = None
    short_name: Optional[str] = None
    opens: Optional[str] = None  # Assuming date/time as string; adjust type as needed
    assessment_start: Optional[str] = None  # Adjust type as needed
    deadline: Optional[str] = None  # Adjust type as needed
    application_reminder_sent: Optional[bool] = None
    reminder_date: Optional[str] = None  # Adjust type as needed
    assessment_deadline: Optional[str] = None  # Adjust type as needed
    prospectus: Optional[str] = None
    privacy_notice: Optional[str] = None
    reference_contact_page_over_email: Optional[bool] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_textphone: Optional[str] = None
    support_times: Optional[str] = None
    support_days: Optional[str] = None
    instructions_json: Optional[Dict[str, str]] = None  # Assuming simple dict; adjust as needed
    feedback_link: Optional[str] = None
    project_name_field_id: Optional[str] = None
    application_guidance_json: Optional[Dict[str, str]] = None  # Adjust as needed
    guidance_url: Optional[str] = None
    all_uploaded_documents_section_available: Optional[bool] = None
    application_fields_download_available: Optional[bool] = None
    display_logo_on_pdf_exports: Optional[bool] = None
    mark_as_complete_enabled: Optional[bool] = None
    is_expression_of_interest: Optional[bool] = None
    eoi_decision_schema: Optional[str] = None  # Adjust type as
    feedback_survey_config: FeedbackSurveyConfig = field(default_factory=FeedbackSurveyConfig)
    eligibility_config: EligibilityConfig = field(default_factory=EligibilityConfig)
    title_json: TitleJson = field(default_factory=TitleJson)
    contact_us_banner_json: ContactUsBannerJson = field(default_factory=ContactUsBannerJson)


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
        owner_organisation_name=fund.owner_organisation.name,
        owner_organisation_shortname=fund.owner_organisation.short_name,
        owner_organisation_logo_uri=fund.owner_organisation.logo_uri,
    )
    write_config(fund_export, "fund_config", round.short_name, "python_file")


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
        reference_contact_page_over_email=False,
    )

    write_config(round_export, "round_config", round.short_name, "python_file")


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
    generate_fund_config(round_id)
    generate_round_config(round_id)
    generate_application_display_config(round_id)
