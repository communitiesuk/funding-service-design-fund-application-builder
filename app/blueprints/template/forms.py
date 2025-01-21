from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired, FileSize
from govuk_frontend_wtf.wtforms_widgets import GovFileInput, GovSubmitInput, GovTextInput
from wtforms import HiddenField, StringField, SubmitField
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
        "Upload a file",
        description="Supports JSON files only",
        widget=GovFileInput(),
        validators=[
            FileRequired(message="File upload is required"),
            FileAllowed(upload_set=["json"], message="Select a file with the extension .json"),
            FileSize(max_size=2 * 1024 * 1024, message="Select a file smaller than 2MB"),
        ],
    )
    save_and_continue = SubmitField("Save and continue", widget=GovSubmitInput())
    save_and_return_home = SubmitField("Save and return home", widget=GovSubmitInput())


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
