from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovSelect, GovSubmitInput, GovTextInput
from wtforms import HiddenField, SelectField, StringField
from wtforms.fields.simple import SubmitField
from wtforms.validators import DataRequired

from app.db.queries.application import get_all_template_forms


class SectionForm(FlaskForm):
    round_id = HiddenField("Round ID")
    section_id = HiddenField("Section ID")
    name_in_apply_en = StringField(
        "Name", widget=GovTextInput(), validators=[DataRequired(message="Enter the section name")]
    )
    template_id = SelectField(
        "Create form from template",
        widget=GovSelect(),
        validators=[DataRequired(message="Select a template")],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [("", "Select a template")]
        for f in get_all_template_forms():
            choices.append((str(f.form_id), f.template_name + " - " + f.name_in_apply_json["en"]))
        self.template_id.choices = choices

    add_form = SubmitField("Add", widget=GovSubmitInput())
    save_section = SubmitField("Save and continue", widget=GovSubmitInput())

    def validate(self, extra_validators=None):
        form_status = True
        if self.save_section.data:
            # render comments for updating section name
            if not self.name_in_apply_en.data or not self.name_in_apply_en.data.strip():
                self.name_in_apply_en.errors = ["Enter section name"]
                form_status = False
        elif self.add_form.data:
            # render comments for adding template forms
            if not self.template_id.data or not self.template_id.data.strip():
                self.template_id.errors = ["Select a template"]
                form_status = False

        return form_status


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
