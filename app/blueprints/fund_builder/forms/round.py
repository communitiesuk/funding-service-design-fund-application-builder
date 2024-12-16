import datetime
import json
import re

from flask_wtf import FlaskForm
from flask_wtf import Form
from wtforms import FormField
from wtforms import HiddenField
from wtforms import RadioField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import URLField
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import ValidationError

from app.db.queries.fund import get_fund_by_id
from app.db.queries.round import get_round_by_short_name_and_fund_id
from app.shared.helpers import no_spaces_between_letters


def validate_json_field(form, field):
    str_content = field.data
    if not str_content:
        return
    try:
        json.loads(str_content)
    except Exception as ex:
        raise ValidationError(f"Content is not valid JSON. Underlying error: [{str(ex)}]")


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
    if form.data and field.data and form.data.get('fund_id'):
        rond_data = get_round_by_short_name_and_fund_id(form.data.get('fund_id'), field.data)
        if rond_data and str(rond_data.round_id) != form.data.get('round_id'):
            fund_data = get_fund_by_id(form.data.get('fund_id'))
            raise ValidationError(f'Given short name already exists in the fund {fund_data.title_json.get("en")}.')


def get_datetime(form_field):
    day = int(form_field.day.data)
    month = int(form_field.month.data)
    year = int(form_field.year.data)
    hour = int(form_field.hour.data)
    minute = int(form_field.minute.data)
    try:
        form_field_datetime = datetime.datetime(year, month, day, hour=hour, minute=minute).strftime("%m-%d-%Y %H:%M")
        return form_field_datetime
    except ValueError:
        raise ValidationError(f"Invalid date entered for {form_field}")


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
        except ValueError:
            raise ValidationError("Invalid Day")

    def validate_month(self, field):
        try:
            month = int(field.data)
            if month < 1 or month > 12:
                raise ValidationError("Month must be between 1 and 12")
        except ValueError:
            raise ValidationError("Invalid month")

    def validate_year(self, field):
        try:
            int(field.data)
        except ValueError:
            raise ValidationError("Invalid Year")

    def validate_hour(self, field):
        try:
            hour = int(field.data)
            if hour < 0 or hour > 23:
                raise ValidationError("Hour must be between 0 and 23 inclusive.")
        except ValueError:
            raise ValidationError("Invalid Day")

    def validate_minute(self, field):
        try:
            minute = int(field.data)
            if minute < 0 or minute >= 60:
                raise ValidationError("Minute must be between 0 and 59 inclusive.")
        except ValueError:
            raise ValidationError("Invalid Day")


class RoundForm(FlaskForm):

    JSON_FIELD_HINT = "Valid json format, using double quotes, lowercase true/false"

    round_id = HiddenField("Round ID")
    fund_id = StringField("Fund", validators=[DataRequired()])
    title_en = StringField("Title (English)", validators=[DataRequired()])
    title_cy = StringField("Title (Welsh)", description="Leave blank for English-only funds")
    short_name = StringField(
        "Short name",
        description="Choose a unique short name with 6 or fewer characters",
        validators=[DataRequired(), Length(max=6), no_spaces_between_letters, validate_unique_round_short_name],
    )
    opens = FormField(DateInputForm, label="Opens")
    deadline = FormField(DateInputForm, label="Deadline")
    assessment_start = FormField(DateInputForm, label="Assessment start date")
    reminder_date = FormField(DateInputForm, label="Reminder date")
    assessment_deadline = FormField(DateInputForm, label="Assessment deadline")
    prospectus_link = URLField("Prospectus link", validators=[DataRequired(), validate_flexible_url])
    privacy_notice_link = URLField("Privacy notice link", validators=[DataRequired(), validate_flexible_url])
    application_reminder_sent = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    contact_us_banner_en = TextAreaField(
        "Contact Us banner (English)", description="HTML to display to override the default 'Contact Us' page content"
    )
    contact_us_banner_cy = TextAreaField("Contact Us banner (Welsh)", description="Leave blank for English-only funds")
    reference_contact_page_over_email = RadioField(
        "Reference contact page over email", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    contact_email = StringField("Grant team email address")
    contact_phone = StringField("Grant team phone number")
    contact_textphone = StringField("Grant team text phone number")
    support_times = StringField("Support times for applicants", validators=[DataRequired()])
    support_days = StringField("Support days", validators=[DataRequired()])
    instructions_en = TextAreaField("Instructions (English)")
    instructions_cy = StringField("Instructions (Welsh)", description="Leave blank for English-only funds")
    feedback_link = URLField("Feedback link", validators=[validate_flexible_url])
    project_name_field_id = StringField("Project name field ID", validators=[DataRequired()])
    application_guidance_en = TextAreaField("Application guidance (English)")
    application_guidance_cy = TextAreaField(
        "Application guidance (Welsh)", description="Leave blank for English-only funds"
    )
    guidance_url = URLField("Guidance link", validators=[validate_flexible_url])
    all_uploaded_documents_section_available = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    application_fields_download_available = RadioField(
        "Application fields download available", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    display_logo_on_pdf_exports = RadioField(
        "Display logo on PDF exports", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    mark_as_complete_enabled = RadioField(
        "Mark as complete enabled", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    is_expression_of_interest = RadioField(
        "Is expression of interest", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    has_feedback_survey = RadioField("Has feedback survey", choices=[("true", "Yes"), ("false", "No")], default="false")
    has_section_feedback = RadioField(
        "Has section feedback", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    has_research_survey = RadioField("Has research survey", choices=[("true", "Yes"), ("false", "No")], default="false")
    is_feedback_survey_optional = RadioField(
        "Is feedback survey optional", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    is_section_feedback_optional = RadioField(
        "Is section feedback optional", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    is_research_survey_optional = RadioField(
        "Is research survey optional", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    eligibility_config = RadioField(
        "Has eligibility config", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    eoi_decision_schema_en = TextAreaField(
        "EOI decision schema (English)", validators=[validate_json_field], description=JSON_FIELD_HINT
    )
    eoi_decision_schema_cy = TextAreaField(
        "EOI decision schema (Welsh)",
        description="Leave blank for English-only funds",
        validators=[validate_json_field],
    )
