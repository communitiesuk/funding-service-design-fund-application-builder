from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectMultipleField, StringField
from wtforms.validators import InputRequired


class FormForm(FlaskForm):
    id = HiddenField()
    builder_display_name = StringField(
        label="Display Name in this tool",
        validators=[InputRequired(message="Supply a name for this form in this tool")],
    )
    form_title = StringField(label="Form Title", validators=[InputRequired(message="Supply a title for this form")])
    start_page_guidance = StringField(label="Start page guidance")
    selected_pages = SelectMultipleField(validate_choice=False)

    def as_dict(self):
        return {field_name: field.data for field_name, field in self._fields.items()}
