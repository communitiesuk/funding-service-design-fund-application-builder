from enum import Enum

from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms import RadioField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired, ValidationError
from wtforms.validators import Length

from app.db.models.fund import FundingType
from app.db.queries.fund import get_fund_by_short_name
from app.shared.helpers import no_spaces_between_letters


def validate_unique_fund_short_name(form, field):
    if field.data and form.data:
        fund_data = get_fund_by_short_name(field.data)
        if fund_data and str(fund_data.fund_id) != form.data.get('fund_id'):
            raise ValidationError('Given fund short name already exists.')


class GovUkRadioEnumField(RadioField):
    source_enum: Enum
    gov_uk_choices: list

    def __init__(self, name: str, _prefix, _translations, label: str, _form, source_enum: Enum):
        super().__init__(
            name=name,
            label=label,
            _form=_form,
            _prefix=_prefix,
            _translations=_translations,
            choices=[(value.name, value.value) for value in source_enum],
        )
        self.source_enum = source_enum
        self.gov_uk_choices = [
            {"text": value.get_text_for_display(), "value": value.value} for value in self.source_enum
        ]


class FundForm(FlaskForm):
    fund_id = HiddenField("Fund ID")
    name_en = StringField("Name (English)", validators=[DataRequired()])
    name_cy = StringField("Name (Welsh)")
    title_en = StringField("Title (English)", validators=[DataRequired()])
    title_cy = StringField("Title (Welsh)")
    short_name = StringField("Short name", validators=[DataRequired(), Length(max=10), no_spaces_between_letters,
                                                       validate_unique_fund_short_name])
    description_en = TextAreaField("Description", validators=[DataRequired()])
    description_cy = TextAreaField("Description (Welsh)")
    welsh_available = RadioField("Welsh available", choices=[("true", "Yes"), ("false", "No")], default="false")
    funding_type = GovUkRadioEnumField(label="Funding type", source_enum=FundingType)
    ggis_scheme_reference_number = StringField("GGIS scheme reference number", validators=[Length(max=255)])
