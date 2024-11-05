from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms import HiddenField
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Regexp


class TemplateUploadForm(FlaskForm):
    template_name = StringField("Template Name", validators=[DataRequired()])
    file = FileField("Upload File", validators=[DataRequired()])


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
