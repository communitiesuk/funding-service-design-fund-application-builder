from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms import StringField
from wtforms.validators import DataRequired


class CriteriaForm(FlaskForm):
    round_id = HiddenField("Round ID")
    criteria_id = HiddenField("Criteria ID")
    name = StringField("Name", validators=[DataRequired()])
    weighting = StringField("Weighting", validators=[DataRequired()])
