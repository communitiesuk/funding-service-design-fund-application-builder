from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms import StringField
from wtforms.validators import DataRequired


class ThemeForm(FlaskForm):
    theme_id = HiddenField("Theme ID")
    subcriteria_id = HiddenField("Subcriteria ID")
    name = StringField("Name", validators=[DataRequired()])
