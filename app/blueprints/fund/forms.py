from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovRadioInput, GovTextArea, GovTextInput
from wtforms import HiddenField, RadioField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError

from app.db.models.fund import FundingType
from app.db.queries.fund import get_fund_by_short_name
from app.shared.helpers import no_spaces_between_letters


def validate_unique_fund_short_name(form, field):
    if field.data and form.data:
        fund_data = get_fund_by_short_name(field.data)
        if fund_data and str(fund_data.fund_id) != form.data.get("fund_id"):
            raise ValidationError("Given fund short name already exists.")


class FundForm(FlaskForm):
    fund_id = HiddenField("Fund ID")
    name_en = StringField("Grant name", widget=GovTextInput(), validators=[DataRequired()])
    name_cy = StringField("Grant name (Welsh)", widget=GovTextInput())
    title_en = StringField("Application heading", widget=GovTextInput(), validators=[DataRequired()])
    title_cy = StringField("Application heading (Welsh)", widget=GovTextInput())
    short_name = StringField(
        "Short name",
        widget=GovTextInput(),
        validators=[DataRequired(), Length(max=10), no_spaces_between_letters, validate_unique_fund_short_name],
    )
    description_en = TextAreaField("Description", widget=GovTextArea(), validators=[DataRequired()])
    description_cy = TextAreaField("Description (Welsh)", widget=GovTextArea())
    welsh_available = RadioField(
        "Welsh available", widget=GovRadioInput(), choices=[("true", "Yes"), ("false", "No")], default="false"
    )
    funding_type = RadioField(
        label="Funding type",
        widget=GovRadioInput(),
        choices=[(value.value, value.get_text_for_display()) for value in FundingType],
    )
    ggis_scheme_reference_number = StringField(
        "GGIS scheme reference number", widget=GovTextInput(), validators=[Length(max=255)]
    )
