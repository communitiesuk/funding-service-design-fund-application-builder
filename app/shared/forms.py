from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSelect, GovSubmitInput
from wtforms import SelectField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired


class SelectFundForm(FlaskForm):
    fund_id = SelectField(
        "Select or add a grant",
        widget=GovSelect(),
        validators=[DataRequired(message="Select or add a grant")],
    )


class DeleteConfirmationForm(FlaskForm):
    delete = SubmitField("Yes, delete", widget=GovSubmitInput())
