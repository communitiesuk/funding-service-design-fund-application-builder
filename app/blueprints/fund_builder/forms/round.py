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
    round_id = HiddenField("Round ID")
    fund_id = StringField("Fund", validators=[DataRequired()])
    title_en = StringField("Title", validators=[DataRequired()])
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
    contact_us_banner_json = TextAreaField("Contact Us Banner")
    reference_contact_page_over_email = RadioField(
        "Reference contact page over email", choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    contact_email = StringField("Contact Email", validators=[DataRequired()])
    contact_phone = StringField("Contact Phone", validators=[DataRequired()])
    contact_textphone = StringField("Contact Textphone", validators=[DataRequired()])
    support_times = StringField("Support times", validators=[DataRequired()])
    support_days = StringField("Support Days", validators=[DataRequired()])
    instructions_json = TextAreaField("Instructions")
    feedback_link = URLField("Prospectus Link", validators=[DataRequired(), URL()])
    project_name_field_id = StringField("Project name", validators=[DataRequired()])
    application_guidance_json = TextAreaField("Application Guidance")
    guidance_url = URLField("Guidance link", validators=[DataRequired(), URL()])
    all_uploaded_documents_section_available = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    application_fields_download_available = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    display_logo_on_pdf_exports = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    mark_as_complete_enabled = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    is_expression_of_interest = RadioField(choices=[("true", "Yes"), ("false", "No")], default="false")
    feedback_survey_config = TextAreaField("Feedback Survey")
    eligibility_config = TextAreaField("Eligibility config")
    eoi_decision_schema = TextAreaField("EOI Decision schema")
