from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms import StringField
from wtforms.validators import DataRequired


class TemplateUploadForm(FlaskForm):
    template_name = StringField("Template Name", validators=[DataRequired()])
    file = FileField("Upload File", validators=[DataRequired()])
