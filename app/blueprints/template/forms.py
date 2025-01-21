from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovFileInput, GovTextInput
from wtforms import FileField, HiddenField, StringField
from wtforms.validators import DataRequired, Regexp


class TemplateCreateForm(FlaskForm):
    template_name = StringField("Template name", widget=GovTextInput(), validators=[DataRequired()])
    tasklist_name = StringField(
        "Task name",
        widget=GovTextInput(),
        description="For example, Project management. Applicants will see this in the application",
        validators=[DataRequired()],
    )
    file = FileField(
        "Upload a file", description="Supports JSON files only", widget=GovFileInput(), validators=[DataRequired()]
    )


class TemplateFormForm(FlaskForm):
    form_id = HiddenField()

    template_name = StringField(
        "Template Name",
        description="Name of this template, only used in FAB",
        validators=[DataRequired()],
    )
    tasklist_name = StringField(
        "Tasklist Name",
        description="Name that appears for this form in the tasklist (applicants will see this)",
        validators=[DataRequired()],
    )
    url_path = StringField(
        "URL Path",
        description="The portion of the URL that equates to the form name. Use only letters, numbers and hyphens (-)",
        validators=[
            DataRequired(),
            Regexp("^[a-z0-9-]*$", message="URL Path must only contain lowercase letters, numbers and hyphens (-)"),
        ],
    )
