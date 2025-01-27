from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovRadioInput, GovSubmitInput, GovTextArea, GovTextInput
from wtforms import HiddenField, RadioField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from app.db.models.fund import FundingType
from app.db.queries.fund import get_fund_by_short_name
from app.shared.validators import NoSpacesBetweenLetters


def validate_unique_fund_short_name(form, field):
    if field.data and form.data:
        fund_data = get_fund_by_short_name(field.data)
        if fund_data and str(fund_data.fund_id) != form.data.get("fund_id"):
            raise ValidationError("Grant short name must be unique")


class FundForm(FlaskForm):
    fund_id = HiddenField("Fund ID")
    welsh_available = RadioField(
        "Is this grant available in Welsh?",
        choices=[("true", "Yes"), ("false", "No")],
        coerce=lambda value: value == "true",
        widget=GovRadioInput(),
        default="false",
        render_kw={"class": "govuk-radios govuk-radios--inline"},
    )
    name_en = StringField(
        "Grant name",
        widget=GovTextInput(),
        description="For example, Community Ownership Fund",
        validators=[DataRequired(message="Enter the grant name")],
    )
    name_cy = StringField(
        "Grant name (Welsh)", widget=GovTextInput(), description="For example, Community Ownership Fund"
    )
    short_name = StringField(
        "Grant short name",
        widget=GovTextInput(),
        description="A unique acronym of up to 10 characters for the grant. For example, COF",
        validators=[
            DataRequired(message="Enter the grant short name"),
            Length(max=10, message="Grant short name must be a maximum of 10 characters"),
            NoSpacesBetweenLetters(message="Grant short name must not have spaces between characters"),
            validate_unique_fund_short_name,
        ],
    )
    title_en = StringField(
        "Application name",
        widget=GovTextInput(),
        description="For example, Apply for funding to save an asset in your community",
        validators=[DataRequired(message="Enter the application heading")],
    )
    title_cy = StringField(
        "Application name (Welsh)",
        widget=GovTextInput(),
        description="For example, Apply for funding to save an asset in your community",
    )
    description_en = TextAreaField(
        "Description",
        widget=GovTextArea(),
        description="What the grant is for. You can find this in the grant prospectus",
        validators=[DataRequired(message="Enter the grant description")],
    )
    description_cy = TextAreaField(
        "Description (Welsh)",
        widget=GovTextArea(),
        description="What the grant is for. You can find this in the grant prospectus",
    )

    funding_type = RadioField(
        "Funding type",
        choices=[(choice.value, choice.get_text_for_display()) for choice in FundingType],
        widget=GovRadioInput(),
        validators=[DataRequired(message="Select the funding type")],
    )
    ggis_scheme_reference_number = StringField(
        "GGIS scheme reference number",
        widget=GovTextInput(),
        validators=[Length(max=255, message="GGIS scheme reference number must be a maximum of 255 characters")],
    )
    save_and_continue = SubmitField("Save and continue", widget=GovSubmitInput())
    save_and_return_home = SubmitField("Save and return home", widget=GovSubmitInput())
