from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, EmailField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, ValidationError



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Length(min=1, max=64), Email()])
    username = StringField(label='Username', validators=[DataRequired(), Length(1, 64), Regexp(
        regex='^[A-Za-z][A-Za-z0-9_.]*$', flags=0,
        message='Username must only have letters, numbers, dots or underscore')])
    password = PasswordField(label='Password', validators=[DataRequired(),
                                                           EqualTo(fieldname='password2',
                                                                   message='passwords must match'),
                                                           ])
    password2 = PasswordField(label='Confirm password', validators=[DataRequired()])
    submit = SubmitField(label='Register')

    def validate_email(self, field):
        from ..models import User
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(message='Email is already registered')

    def validate_username(self, field):
        from ..models import User
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(message='Username is already taken by someone else.')


class PasswordUpdateForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Length(min=1, max=64), Email()], render_kw = {'readonly': True})
    username = StringField(label='Username', validators=[DataRequired(), Length(1, 64), Regexp(
        regex='^[A-Za-z][A-Za-z0-9_.]*$', flags=0,
        message='Username must only have letters, numbers, dots or underscore')], render_kw = {'readonly': True})
    password = PasswordField(label='Password', validators=[DataRequired(),
                                                           EqualTo(fieldname='password2',
                                                                   message='passwords must match'),
                                                           ])
    password2 = PasswordField(label='Confirm password', validators=[DataRequired()])
    submit = SubmitField(label='Update')


class PasswordResetRequest(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Length(min=1, max=64), Email()])
    submit = SubmitField(label='Send Link')


class EmailUpdateRequest(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(1, 64), Regexp(
        regex='^[A-Za-z][A-Za-z0-9_.]*$', flags=0,
        message='Username must only have letters, numbers, dots or underscore')], render_kw={'readonly': True})
    email = StringField(label='Old Email', validators=[DataRequired(), Length(min=1, max=64), Email()], render_kw={'readonly': True})
    email2 = StringField(label='New Email', validators=[DataRequired(), Length(min=1, max=64), Email()])
    submit = SubmitField(label='Send Link')

    def validate_email(self, field):
        if field.data == self.email2.data:
            raise ValidationError(message='New Email address cannot be same as old email address')
