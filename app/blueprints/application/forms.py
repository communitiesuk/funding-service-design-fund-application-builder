from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSelect, GovTextInput
from wtforms import HiddenField, SelectField, StringField
from wtforms.validators import DataRequired


class SectionForm(FlaskForm):
    round_id = HiddenField("Round ID")
    section_id = HiddenField("Section ID")
    name_in_apply_en = StringField("Name", widget=GovTextInput(), validators=[DataRequired()])


class SelectApplicationForm(FlaskForm):
    round_id = SelectField(
        "Select or create an application",
        widget=GovSelect(),
        validators=[DataRequired(message="Select or create an application")],
    )

    def __init__(self, fund, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [("", "Select an application")]
        for round_ in fund.rounds:
            choices.append((str(round_.round_id), round_.short_name + " - " + round_.title_json["en"]))
        self.round_id.choices = choices
