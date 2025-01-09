from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, StringField
from wtforms.validators import DataRequired


class SectionForm(FlaskForm):
    round_id = HiddenField("Round ID")
    section_id = HiddenField("Section ID")
    name_in_apply_en = StringField("Name", validators=[DataRequired()])


class SelectApplicationForm(FlaskForm):
    round_id = SelectField(
        "Select or create an application", validators=[DataRequired(message="Select or create an application")]
    )
