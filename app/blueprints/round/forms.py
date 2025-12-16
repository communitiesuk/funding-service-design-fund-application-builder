from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovRadioInput, GovSubmitInput, GovTextArea, GovTextInput
from wtforms import HiddenField, RadioField, StringField, SubmitField, TextAreaField, URLField
from wtforms.fields.datetime import DateTimeField
from wtforms.validators import DataRequired, InputRequired, Length, Optional, ValidationError

from app.db.queries.round import get_round_by_short_name_and_fund_id
from app.shared.validators import FlexibleUrl, JsonValidation, NoSpacesBetweenLetters, WelshJsonValidation
from govuk_frontend_ext.fields import GovDatetimeInput


def validate_unique_round_short_name(form, field):
    if form.data and field.data and form.data.get("fund_id"):
        rond_data = get_round_by_short_name_and_fund_id(form.data.get("fund_id"), field.data)
        if rond_data and str(rond_data.round_id) != form.data.get("round_id"):
            raise ValidationError("Application round short name already exists for this grant")


class RoundForm(FlaskForm):
    JSON_FIELD_HINT = "Valid json format, using double quotes, lowercase true/false"

    round_id = HiddenField("Round ID")
    fund_id = HiddenField("Fund", validators=[DataRequired()])
    welsh_available = HiddenField("Welsh Available")
    title_en = StringField(
        "Application round",
        widget=GovTextInput(),
        description="For example, Round 3",
        validators=[DataRequired(message="Enter the application round")],
    )
    title_cy = StringField(
        "Application round (Welsh)",
        widget=GovTextInput(),
        description="For example, Round 3",
    )
    short_name = StringField(
        "Round short name",
        widget=GovTextInput(),
        description="Choose a unique short name with a maximum of 6 characters",
        validators=[
            DataRequired(message="Enter the round short name"),
            Length(max=6, message="Application short name must be a maximum of 6 characters"),
            NoSpacesBetweenLetters(message="Application short name must not have spaces between characters"),
            validate_unique_round_short_name,
        ],
    )
    opens = DateTimeField(
        "Application round opens",
        widget=GovDatetimeInput(),
        description=(
            "Dates must be between Tuesday to Thursday (no bank holidays or weekends). The default time is midday - any"
            " bespoke times must be during working hours (9am to 5pm)"
        ),
        format="%d %m %Y %H %M",
        validators=[DataRequired(message="Enter the date and time the application round opens")],
    )
    deadline = DateTimeField(
        "Application round closes",
        widget=GovDatetimeInput(),
        description=(
            "Dates must be between Tuesday to Thursday (no bank holidays or weekends). The default time is midday - any"
            " bespoke times must be during working hours (9am to 5pm)"
        ),
        format="%d %m %Y %H %M",
        validators=[DataRequired(message="Enter the date and time the application round closes")],
    )
    reminder_date = DateTimeField(
        "Application reminder email",
        widget=GovDatetimeInput(),
        format="%d %m %Y %H %M",
        validators=[DataRequired(message="Enter the date and time for the applicant reminder email")],
    )
    assessment_start = DateTimeField(
        "Assessment opens",
        widget=GovDatetimeInput(),
        format="%d %m %Y %H %M",
        validators=[DataRequired(message="Enter the date and time the assessment opens")],
    )
    assessment_deadline = DateTimeField(
        "Assessment closes",
        widget=GovDatetimeInput(),
        format="%d %m %Y %H %M",
        validators=[DataRequired(message="Enter the date and time the assessment closes")],
    )
    guidance_url = URLField(
        "Assessor guidance link (optional)",
        widget=GovTextInput(),
        validators=[
            FlexibleUrl(
                message="Assessor guidance link must be in the correct website format. "
                "For example, www.sharepoint.co.uk/assessorguidance"
                # noqa: E501
            )
        ],
    )
    contact_email = StringField("Grant team email address (optional)", widget=GovTextInput())
    instructions_en = TextAreaField("Before you apply guidance (optional)", widget=GovTextArea())
    instructions_cy = StringField("Before you apply guidance (Welsh) (optional)", widget=GovTextInput())
    application_guidance_en = TextAreaField("Completing the application guidance (optional)", widget=GovTextArea())
    application_guidance_cy = TextAreaField(
        "Completing the application guidance (Welsh) (optional)", widget=GovTextArea()
    )
    feedback_link = URLField(
        "Feedback link (optional)",
        widget=GovTextInput(),
        validators=[
            FlexibleUrl(
                message="Feedback link must be in the correct website format. For example, "
                "www.grantapplicationfeedback.com"
                # noqa: E501
            )
        ],
    )
    prospectus_link = URLField(
        "Prospectus link",
        widget=GovTextInput(),
        validators=[
            DataRequired(message="Enter the prospectus link"),
            FlexibleUrl(
                message="Prospectus link must be in the correct website format. For example, www.grantprospectus.com"
            ),
            # noqa: E501
        ],
    )
    privacy_notice_link = URLField(
        "Privacy notice link",
        widget=GovTextInput(),
        validators=[
            DataRequired(message="Enter the privacy notice link"),
            FlexibleUrl(
                message="Privacy notice must be in the correct website format. For example, www.grant.com/privacynotice"
            ),
        ],
    )
    project_name_field_id = StringField(
        "Project name field ID",
        widget=GovTextInput(),
        description="Ask a developer on the Forms team for the correct field ID",
        validators=[DataRequired(message="Enter the project name field ID")],
    )
    eoi_decision_schema_en = TextAreaField(
        "Expression of interest decision schema (optional)",
        widget=GovTextArea(),
        validators=[Optional(), JsonValidation()],
        description=JSON_FIELD_HINT,
    )
    eoi_decision_schema_cy = TextAreaField(
        "Expression of interest decision schema (Welsh) (optional)",
        widget=GovTextArea(),
        description=JSON_FIELD_HINT,
        validators=[Optional(), WelshJsonValidation()],
    )
    application_fields_download_available = RadioField(
        "Do you want to allow assessors to download application fields?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select whether you want to allow assessors to download application fields")],
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
    )
    display_logo_on_pdf_exports = RadioField(
        "Do you want to have the MHCLG logo on PDFs?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select whether you want to display the MHCLG logo on PDFs")],
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
    )
    mark_as_complete_enabled = RadioField(
        "Do you want applicants to mark sections as complete?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select whether you want applicants to mark sections as complete")],
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
    )
    is_expression_of_interest = RadioField(
        "Is this application round an expression of interest?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select whether this application round is an expression of interest")],
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
    )
    has_feedback_survey = RadioField(
        "Do you want to include a feedback survey?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select whether you want to include a feedback survey")],
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
    )
    is_feedback_survey_optional = RadioField(
        "Is the feedback survey optional?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select whether the feedback survey is optional")],
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
    )
    has_research_survey = RadioField(
        "Do you want to include a research survey?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select whether you want to include a research survey")],
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
    )
    is_research_survey_optional = RadioField(
        "Is the research survey optional?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select whether the research survey is optional")],
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
    )
    eligibility_config = RadioField(
        "Do applicants need to pass eligibility questions before applying?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select whether applicants need to pass eligibility questions")],
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
    )
    send_incomplete_application_emails = RadioField(
        "Do you want to automatically send notification emails for incomplete applications after the deadline?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select whether to send notification emails for incomplete applications")],
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value if isinstance(value, bool) else value == "true",
    )
    save_and_continue = SubmitField("Save and continue", widget=GovSubmitInput())
    save_and_return_home = SubmitField("Save and return home", widget=GovSubmitInput())

    def validate(self, extra_validators=None):
        form_status = super().validate(extra_validators)
        # Convert welsh_available string to boolean
        if isinstance(self.welsh_available.data, str):
            self.welsh_available.data = self.welsh_available.data == "True"

        # If Welsh is available, validate Welsh fields
        if self.welsh_available.data and not self.title_cy.data.strip():
            self.title_cy.errors.append("Enter the Welsh application round")
            form_status = False

        # Validate that the application closing date is after the opening date
        if self.opens.data and self.deadline.data:
            if self.deadline.data <= self.opens.data:
                self.opens.errors.append(
                    "The date the application round opens must be before the date the application closes"
                )
                self.deadline.errors.append(
                    "The date the application round closes must be after the date the application opens"
                )
                form_status = False

        # Validate that the assessment closing date is after the assessment start date
        if self.assessment_start.data and self.assessment_deadline.data:
            if self.assessment_deadline.data <= self.assessment_start.data:
                self.assessment_start.errors.append(
                    "The date the assessment opens must be before the date the assessment closes"
                )
                self.assessment_deadline.errors.append(
                    "The date the assessment closes must be after the date the assessment opens"
                )
                form_status = False

        return form_status  # Return True only if all validations pass


class CloneRoundForm(FlaskForm):
    fund_id = HiddenField("Fund", validators=[DataRequired()])
