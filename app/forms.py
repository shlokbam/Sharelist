# forms.py - Add the new forms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, HiddenField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, URL, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PlaylistForm(FlaskForm):
    title = StringField('Playlist Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description (Optional)', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Create Playlist')

class LinkForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired(), URL()])
    title = StringField('Custom Title (Optional)', validators=[Optional(), Length(max=200)])
    note = TextAreaField('Notes (Optional)', validators=[Optional(), Length(max=500)])
    playlist_id = HiddenField('Playlist ID')
    submit = SubmitField('Add Link')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    submit = SubmitField('Search')

# New forms for workspace functionality
class CreateWorkspaceForm(FlaskForm):
    name = StringField('Workspace Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Create Workspace')

class JoinWorkspaceForm(FlaskForm):
    share_code = StringField('Share Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Join Workspace')

class SharePlaylistForm(FlaskForm):
    workspace_id = SelectField('Select Workspace', coerce=int)
    submit = SubmitField('Share Playlist')

    def __init__(self, *args, **kwargs):
        super(SharePlaylistForm, self).__init__(*args, **kwargs)
        # Workspace choices will be set dynamically when the form is created