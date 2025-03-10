from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSelect
from wtforms import SelectField
from wtforms.validators import DataRequired


class SelectFundForm(FlaskForm):
    fund_id = SelectField(
        "Select or add a grant",
        widget=GovSelect(),
        validators=[DataRequired(message="Select or add a grant")],
    )
