from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import HiddenField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Length


class FundForm(FlaskForm):
    fund_id = HiddenField("Fund ID", validators=[DataRequired()])
    name_en = StringField("Name", validators=[DataRequired()])
    title_en = StringField("Title", validators=[DataRequired()])
    short_name = StringField("Short Name", validators=[DataRequired(), Length(max=6)])
    description_en = StringField("Description", validators=[DataRequired()])
    welsh_available = BooleanField("Welsh Available")
