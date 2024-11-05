import datetime

from flask_wtf import FlaskForm
from flask_wtf import Form
from wtforms import FormField
from wtforms import HiddenField
from wtforms import RadioField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms import URLField
from wtforms.validators import URL
from wtforms.validators import DataRequired
from wtforms.validators import Length
from wtforms.validators import ValidationError
import json


def validate_json_field(form, field):
    str_content = field.data
    if not str_content:
        return
    try:
        json.loads(str_content)
    except Exception as ex:
        raise ValidationError(f"Content is not valid JSON. Underlying error: [{str(ex)}]")


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
    title_en = StringField("Title (en)", validators=[DataRequired()])
    title_cy = StringField("Title (cy)", description="Leave blank for English-only funds")
    short_name = StringField(
        "Short Name",
        description="Choose a unique short name with 6 or fewer characters",
        validators=[DataRequired(), Length(max=6)],
    )
    opens = FormField(DateInputForm, label="Opens")
    deadline = FormField(DateInputForm, label="Deadline")
    assessment_start = FormField(DateInputForm, label="Assessment Start Date")
    reminder_date = FormField(DateInputForm, label="Reminder Date")
    assessment_deadline = FormField(DateInputForm, label="Assessment Deadline")
    prospectus_link = URLField("Prospectus Link", validators=[DataRequired(), URL()])
    privacy_notice_link = URLField("Privacy Notice Link", validators=[DataRequired(), URL()])
    application_reminder_sent = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    contact_us_banner_en = TextAreaField(
        "Contact Us Banner (en)", description="HTML to display to override the default 'Contact Us' page content"
    )
    contact_us_banner_cy = TextAreaField("Contact Us Banner (cy)", description="Leave blank for English-only funds")
    reference_contact_page_over_email = RadioField(
        "Reference contact page over email", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    contact_email = StringField("Contact Email")
    contact_phone = StringField("Contact Phone")
    contact_textphone = StringField("Contact Textphone")
    support_times = StringField("Support times", validators=[DataRequired()])
    support_days = StringField("Support Days", validators=[DataRequired()])
    instructions_en = TextAreaField("Instructions (en)")
    instructions_cy = StringField("Instructions (cy)", description="Leave blank for English-only funds")
    feedback_link = URLField("Feedback Link", validators=[DataRequired(), URL()])
    project_name_field_id = StringField("Project name field ID", validators=[DataRequired()])
    application_guidance_en = TextAreaField("Application Guidance (en)")
    application_guidance_cy = TextAreaField(
        "Application Guidance (cy)", description="Leave blank for English-only funds"
    )
    guidance_url = URLField("Guidance link", validators=[DataRequired(), URL()])
    all_uploaded_documents_section_available = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    application_fields_download_available = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    display_logo_on_pdf_exports = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    mark_as_complete_enabled = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    is_expression_of_interest = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    feedback_survey_config = TextAreaField(
        "Feedback Survey", validators=[validate_json_field], description=JSON_FIELD_HINT
    )
    eligibility_config = RadioField(
        "Has eligibility config", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    eoi_decision_schema_en = TextAreaField(
        "EOI Decision schema (en)", validators=[validate_json_field], description=JSON_FIELD_HINT
    )
    eoi_decision_schema_cy = TextAreaField(
        "EOI Decision schema (cy)", description="Leave blank for English-only funds", validators=[validate_json_field]
    )
