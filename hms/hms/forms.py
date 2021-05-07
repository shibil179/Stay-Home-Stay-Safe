from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, SelectMultipleField, widgets, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from hms.models import User


class checkbox(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class validate_emails(object):
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
      try:
        user = User.query.filter_by(email=field.data).first()
        print('field.data', field.data)
        message = self.message
        if(user):
            if message is None:
                message = field.gettext('Account is already Registered!')
            #flash('Please, Do not use the Symbols', 'danger     ')
            raise ValidationError(message)
      except:
        pass

class RegistrationForm(FlaskForm):

    name = StringField('Name',
                        validators=[DataRequired(), ])
    email = StringField('Email',
                        validators=[DataRequired(), Email(), validate_emails()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    contact_no = StringField('Contact Number',
                           validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Address',
                           validators=[DataRequired(), Length(min=2, max=20)])
    pincode = StringField('Pincode',
                           validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Register')

class RegistrationAdminForm(FlaskForm):

    role = RadioField('Role', choices=['Hospital', 'Doctor'])
    name = StringField('Name',
                        validators=[DataRequired(), ])
    email = StringField('Email',
                        validators=[DataRequired(), Email(), validate_emails()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    contact_no = StringField('Contact Number',
                           validators=[DataRequired(), Length(min=2, max=20)])
    address = StringField('Address',
                           validators=[DataRequired(), Length(min=2, max=20)])
    pincode = StringField('Pincode',
                           validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Register')

class BookingForm(FlaskForm):
    booking = RadioField('What you need...', choices=['Take Covid-19 Test', 'Take Covid-19 Vaccine'])
    submit = SubmitField('Submit')

class ChatForm(FlaskForm):
    message = StringField('Send Message...',
                         validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Send')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

