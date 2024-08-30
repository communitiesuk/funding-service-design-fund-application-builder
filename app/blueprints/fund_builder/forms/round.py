from flask_wtf import FlaskForm
from wtforms import DateTimeField
from wtforms import HiddenField
from wtforms import StringField
from wtforms import URLField
from wtforms.validators import URL
from wtforms.validators import DataRequired
from wtforms.validators import Length


class RoundForm(FlaskForm):
    round_id = HiddenField("Round ID")
    fund_id = StringField("Fund", validators=[DataRequired()])
    title_en = StringField("Title", validators=[DataRequired()])
    short_name = StringField(
        "Short Name",
        description="Choose a unique short name with 6 or fewer characters",
        validators=[DataRequired(), Length(max=6)],
    )
    opens = DateTimeField("Opens", format="%d-%m-%Y %H:%M", validators=[DataRequired()])
    deadline = DateTimeField("Deadline", format="%d-%m-%Y %H:%M", validators=[DataRequired()])
    assessment_start = DateTimeField("Assessment Start", format="%d-%m-%Y %H:%M", validators=[DataRequired()])
    reminder_date = DateTimeField("Reminder Date", format="%d-%m-%Y %H:%M", validators=[DataRequired()])
    assessment_deadline = DateTimeField("Assessment Deadline", format="%d-%m-%Y %H:%M", validators=[DataRequired()])
    prospectus_link = URLField("Prospectus Link", validators=[DataRequired(), URL()])
    privacy_notice_link = URLField("Privacy Notice Link", validators=[DataRequired(), URL()])
