from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, EqualTo
from flask_ckeditor import CKEditorField
from wtforms.widgets import TextArea
from flask_wtf.file import FileField
from flask_wtf import FlaskForm


# Create a Login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Create a User form


class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    about_user = StringField("About User", validators=[
                             DataRequired()], widget=TextArea())
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'password_hash2', message='Passwords must match!')])
    password_hash2 = PasswordField(
        'Confirm Password', validators=[DataRequired()])
    user_profile_pic = FileField("Profile Picture")

    submit = SubmitField('Submit')
    update = SubmitField('Update')
    delete = SubmitField('Delete')


# Create a Blog Posts form
class BlogPostsForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    # content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a form class
class NamerForm(FlaskForm):
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a Test Pass form class
class PasswordForm(FlaskForm):
    email = StringField("What's your Email?", validators=[DataRequired()])
    password_hash = PasswordField(
        "What's your Email?", validators=[DataRequired()])
    submit = SubmitField('Submit')


# Create a Search form class
class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Submit')
