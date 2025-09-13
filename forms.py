from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileAllowed

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ItemForm(FlaskForm):
    name = StringField("Item Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    image = FileField("Upload Image", validators=[FileAllowed(["jpg", "png", "jpeg"])])
    submit = SubmitField("Create Item")
