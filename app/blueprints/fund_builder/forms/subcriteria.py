from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField
from wtforms.validators import DataRequired


class SubcriteriaForm(FlaskForm):
    criteria_id = HiddenField("Criteria ID")
    subcriteria_id = HiddenField("Subcriteria ID")
    name = StringField("Name", validators=[DataRequired()])
