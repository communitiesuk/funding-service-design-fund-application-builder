from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired


class SelectFundForm(FlaskForm):
    fund_id = SelectField("Select or add a grant", validators=[DataRequired(message="Select or add a grant")])
