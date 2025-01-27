import json
import re

from flask_wtf import FlaskForm, Form
from govuk_frontend_wtf.wtforms_widgets import GovRadioInput, GovSubmitInput, GovTextArea, GovTextInput
from wtforms import HiddenField, RadioField, StringField, SubmitField, TextAreaField, URLField
from wtforms.fields.datetime import DateTimeField
from wtforms.validators import DataRequired, Length, ValidationError

from app.db.queries.fund import get_fund_by_id
from app.db.queries.round import get_round_by_short_name_and_fund_id
from app.shared.helpers import no_spaces_between_letters
from govuk_frontend_ext.fields import GovDatetimeInput


def validate_json_field(form, field):
    str_content = field.data
    if not str_content:
        return
    try:
        json.loads(str_content)
    except Exception as ex:
        raise ValidationError(f"Content is not valid JSON. Underlying error: [{str(ex)}]") from ex


def validate_flexible_url(form, field):
    """
    Validates URLs allowing:
    - Optional scheme (http://, https://)
    - Domain names with multiple subdomains
    - Optional paths, query parameters
    - Common TLDs
    - No scheme required
    """
    if not field.data:
        return

    pattern = (
        # Optional scheme
        r"^(?:(?:http|https)://)?"
        # Domain with optional subdomains
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,63})"
        # Optional port
        r"(?::\d+)?"
        # Optional path
        r"(?:/[^/\s]*)*"
        # Optional query string
        r"(?:\?[^\s]*)?"
        # Optional fragment
        r"(?:#[^\s]*)?$"
    )

    if not re.match(pattern, field.data, re.IGNORECASE):
        raise ValidationError("Invalid URL. Please enter a valid web address.")


def validate_unique_round_short_name(form, field):
    if form.data and field.data and form.data.get("fund_id"):
        rond_data = get_round_by_short_name_and_fund_id(form.data.get("fund_id"), field.data)
        if rond_data and str(rond_data.round_id) != form.data.get("round_id"):
            fund_data = get_fund_by_id(form.data.get("fund_id"))
            raise ValidationError(f"Given short name already exists in the fund {fund_data.title_json.get('en')}.")


class DateInputForm(Form):
    day = StringField("Day", validators=[DataRequired(), Length(min=1, max=2)])
    month = StringField("Month", validators=[DataRequired(), Length(min=1, max=2)])
    year = StringField("Year", validators=[DataRequired(), Length(min=1, max=4)])
    hour = StringField("Hour", validators=[DataRequired(), Length(min=1, max=2)])
    minute = StringField("Minute", validators=[DataRequired(), Length(min=1, max=2)])

    def validate_day(self, field):
        try:
            day = int(field.data)
            if day < 1 or day > 31:
                raise ValidationError("Day must be between 1 and 31 inclusive.")
        except ValueError as ex:
            raise ValidationError("Invalid Day") from ex

    def validate_month(self, field):
        try:
            month = int(field.data)
            if month < 1 or month > 12:
                raise ValidationError("Month must be between 1 and 12")
        except ValueError as ex:
            raise ValidationError("Invalid month") from ex

    def validate_year(self, field):
        try:
            int(field.data)
        except ValueError as ex:
            raise ValidationError("Invalid Year") from ex

    def validate_hour(self, field):
        try:
            hour = int(field.data)
            if hour < 0 or hour > 23:
                raise ValidationError("Hour must be between 0 and 23 inclusive.")
        except ValueError as ex:
            raise ValidationError("Invalid Day") from ex

    def validate_minute(self, field):
        try:
            minute = int(field.data)
            if minute < 0 or minute >= 60:
                raise ValidationError("Minute must be between 0 and 59 inclusive.")
        except ValueError as ex:
            raise ValidationError("Invalid Day") from ex


class RoundForm(FlaskForm):
    JSON_FIELD_HINT = "Valid json format, using double quotes, lowercase true/false"

    round_id = HiddenField("Round ID")
    fund_id = HiddenField("Fund", validators=[DataRequired()])
    title_en = StringField(
        "Application round", widget=GovTextInput(), description="For example, Round 3", validators=[DataRequired()]
    )
    title_cy = StringField("Application round (Welsh)", widget=GovTextInput(), description="For example, Round 3")
    short_name = StringField(
        "Round short name",
        widget=GovTextInput(),
        description="Choose a unique short name with a maximum of 6 characters",
        validators=[DataRequired(), Length(max=6), no_spaces_between_letters, validate_unique_round_short_name],
    )
    opens = DateTimeField(
        "Application round opens",
        widget=GovDatetimeInput(),
        format="%d %m %Y %H %M",
        validators=[DataRequired(message="Enter a valid date and time")],
    )
    deadline = DateTimeField(
        "Application round closes",
        widget=GovDatetimeInput(),
        format="%d %m %Y %H %M",
        validators=[DataRequired(message="Enter a valid date and time")],
    )
    reminder_date = DateTimeField(
        "Application reminder email",
        widget=GovDatetimeInput(),
        format="%d %m %Y %H %M",
        validators=[DataRequired(message="Enter a valid date and time")],
    )
    assessment_start = DateTimeField(
        "Assessment opens",
        widget=GovDatetimeInput(),
        format="%d %m %Y %H %M",
        validators=[DataRequired(message="Enter a valid date and time")],
    )
    assessment_deadline = DateTimeField(
        "Assessment closes",
        widget=GovDatetimeInput(),
        format="%d %m %Y %H %M",
        validators=[DataRequired(message="Enter a valid date and time")],
    )
    guidance_url = URLField(
        "Assessor guidance link (optional)", widget=GovTextInput(), validators=[validate_flexible_url]
    )
    contact_email = StringField("Grant team email address (optional)", widget=GovTextInput())
    contact_phone = StringField("Grant team phone number (optional)", widget=GovTextInput())
    contact_textphone = StringField("Grant team text phone number (optional)", widget=GovTextInput())
    support_times = StringField("Grant team support hours", widget=GovTextInput(), validators=[DataRequired()])
    support_days = StringField("Grant team support days", widget=GovTextInput(), validators=[DataRequired()])
    instructions_en = TextAreaField("Before you apply guidance (optional)", widget=GovTextArea())
    instructions_cy = StringField("Before you apply guidance (Welsh) (optional)", widget=GovTextInput())
    application_guidance_en = TextAreaField("Completing the application guidance (optional)", widget=GovTextArea())
    application_guidance_cy = TextAreaField(
        "Completing the application guidance (Welsh) (optional)", widget=GovTextArea()
    )
    feedback_link = URLField("Feedback link (optional)", widget=GovTextInput(), validators=[validate_flexible_url])
    prospectus_link = URLField(
        "Prospectus link", widget=GovTextInput(), validators=[DataRequired(), validate_flexible_url]
    )
    privacy_notice_link = URLField(
        "Privacy notice link", widget=GovTextInput(), validators=[DataRequired(), validate_flexible_url]
    )
    project_name_field_id = StringField(
        "Project name field ID",
        widget=GovTextInput(),
        description="Ask a developer on the Forms team for the correct field ID",
        validators=[DataRequired()],
    )
    eoi_decision_schema_en = TextAreaField(
        "Expression of interest decision schema (optional)",
        widget=GovTextArea(),
        validators=[validate_json_field],
        description=JSON_FIELD_HINT,
    )
    eoi_decision_schema_cy = TextAreaField(
        "Expression of interest decision schema (Welsh) (optional)",
        widget=GovTextArea(),
        description=JSON_FIELD_HINT,
        validators=[validate_json_field],
    )
    contact_us_banner_en = TextAreaField(
        "Contact Us information (optional)",
        widget=GovTextArea(),
        description="HTML to display to override the default 'Contact Us' page content",
    )
    contact_us_banner_cy = TextAreaField(
        "Contact Us information (Welsh) (optional)",
        widget=GovTextArea(),
        description="HTML to display to override the default 'Contact Us' page content",
    )
    reference_contact_page_over_email = RadioField(
        "Do you want to include the contact us page in applicant emails",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    application_fields_download_available = RadioField(
        "Do you want to allow assessors to download application fields?",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    display_logo_on_pdf_exports = RadioField(
        "Do you want to have the MHCLG logo on PDFs?",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    mark_as_complete_enabled = RadioField(
        "Do you want applicants to mark sections as complete?",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    is_expression_of_interest = RadioField(
        "Is this application round an expression of interest?",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    has_feedback_survey = RadioField(
        "Do you want to include a feedback survey?",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    is_feedback_survey_optional = RadioField(
        "Is the feedback survey optional?",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    has_research_survey = RadioField(
        "Do you want to include a research survey?",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    is_research_survey_optional = RadioField(
        "Is research survey optional",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    eligibility_config = RadioField(
        "Do applicants need to pass eligibility questions before applying?",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    has_section_feedback = RadioField(
        "Has section feedback",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    is_section_feedback_optional = RadioField(
        "Is section feedback optional",
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    all_uploaded_documents_section_available = RadioField(
        widget=GovRadioInput(),
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        default="false",
    )
    application_reminder_sent = RadioField(
        widget=GovRadioInput(), choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    save_and_continue = SubmitField("Save and continue", widget=GovSubmitInput())
    save_and_return_home = SubmitField("Save and return home", widget=GovSubmitInput())


class CloneRoundForm(FlaskForm):
    fund_id = HiddenField("Fund", validators=[DataRequired()])
