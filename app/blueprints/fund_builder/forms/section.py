from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms import StringField
from wtforms.validators import DataRequired


class SectionForm(FlaskForm):
    round_id = HiddenField("Round ID")
    section_id = HiddenField("Section ID")
    name_in_apply_en = StringField("Name", validators=[DataRequired()])
