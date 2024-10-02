from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import Optional


@dataclass
class SubCondition:
    field: dict
    operator: str
    value: dict
    coordinator: Optional[str]


@dataclass
class ConditionValue:
    name: str
    conditions: list[SubCondition]


@dataclass
class Condition:
    name: str
    display_name: str
    value: ConditionValue
    destination_page_path: str


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

    def as_dict(self):
        return asdict(self)


@dataclass
class FundSectionSection(FundSectionBase):
    requires_feedback: Optional[bool] = None


@dataclass
class FundSectionForm(FundSectionBase):
    form_name_json: FormNameJson


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
    has_section_feedback: Optional[bool] = False
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

    def as_dict(self):
        return asdict(self)


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
    eoi_decision_schema: Optional[Dict[str, str]] = None
    feedback_survey_config: Optional[Dict[str, bool]] = field(
        default_factory=lambda: {
            "has_feedback_survey": False,
            "has_section_feedback": False,
            "is_feedback_survey_optional": False,
            "is_section_feedback_optional": False,
        }
    )
    eligibility_config: Optional[Dict[str, bool]] = field(default_factory=lambda: {"has_eligibility": False})
    title_json: TitleJson = field(default_factory=TitleJson)
    contact_us_banner_json: Optional[Dict[str, str]] = None

    def as_dict(self):
        return asdict(self)
