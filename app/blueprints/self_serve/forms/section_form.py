from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectMultipleField, StringField
from wtforms.validators import InputRequired


class SectionForm(FlaskForm):
    id = StringField(
        label="Section ID",
        validators=[InputRequired(message="Supply a unique ID")],
    )
    builder_display_name = StringField(
        label="Display Name in this tool",
        validators=[InputRequired(message="Supply a name for this section in this tool")],
    )
    section_display_name = StringField(
        label="Section Name", validators=[InputRequired(message="Supply a name for this section")]
    )
    selected_forms = SelectMultipleField(validate_choice=False)
    index = IntegerField(label="Position of this section")

    def as_dict(self):
        return {field_name: field.data for field_name, field in self._fields.items()}
