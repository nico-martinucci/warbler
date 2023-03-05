from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, EmailField
from wtforms.validators import DataRequired, Email, Length


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired(), Length(max=140)])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('E-mail', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')

class EditProfileForm(FlaskForm):
    """Form for editing an existing users."""

    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('E-mail', validators=[DataRequired()])
    image_url = StringField('(Optional) Image URL')
    header_image_url = StringField('(Optional) Header Image URL')
    location = StringField('(Optional) Location')
    bio = TextAreaField('(Optional) Bio')
    password = PasswordField('Password', validators=[Length(min=6)])

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""

