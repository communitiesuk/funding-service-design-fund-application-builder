from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired, FileSize
from govuk_frontend_wtf.wtforms_widgets import GovFileInput, GovSubmitInput, GovTextInput
from wtforms import HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired


class TemplateCreateForm(FlaskForm):
    template_name = StringField(
        "Template name", widget=GovTextInput(), validators=[DataRequired(message="Enter the template name")]
    )
    tasklist_name = StringField(
        "Task name",
        widget=GovTextInput(),
        description="For example, Project management. Applicants will see this in the application",
        validators=[DataRequired(message="Enter the task name")],
    )
    file = FileField(
        "Upload a file",
        description="Supports JSON files only",
        widget=GovFileInput(),
        validators=[
            FileRequired(message="Choose a template file"),
            FileAllowed(upload_set=["json"], message="Upload a valid JSON file"),
            FileSize(max_size=2 * 1024 * 1024, message="Select a file smaller than 2MB"),
        ],
    )
    save_and_continue = SubmitField("Save and continue", widget=GovSubmitInput())
    save_and_return_home = SubmitField("Save and return home", widget=GovSubmitInput())


class TemplateUpdateForm(TemplateCreateForm):
    form_id = HiddenField()
    file = FileField(
        "Replace template file",
        description="Supports JSON files only",
        widget=GovFileInput(),
        validators=[
            FileAllowed(upload_set=["json"], message="Upload a valid JSON file"),
            FileSize(max_size=2 * 1024 * 1024, message="Select a file smaller than 2MB"),
        ],
    )
