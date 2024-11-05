from enum import Enum

from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms import RadioField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Length

from app.db.models.fund import FundingType


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
    name_en = StringField("Name (en)", validators=[DataRequired()])
    name_cy = StringField("Name (cy)", description="Leave blank for English-only funds")
    title_en = StringField("Title (en)", validators=[DataRequired()])
    title_cy = StringField("Title (cy)", description="Leave blank for English-only funds")
    short_name = StringField("Short Name", validators=[DataRequired(), Length(max=10)])
    description_en = TextAreaField("Description", validators=[DataRequired()])
    description_cy = TextAreaField("Description", description="Leave blank for English-only funds")
    welsh_available = RadioField("Welsh Available", choices=[("true", "Yes"), ("false", "No")], default="false")
    funding_type = GovUkRadioEnumField(label="Funding Type", source_enum=FundingType)
