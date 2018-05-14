from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, RadioField, FloatField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, NumberRange
from app.models import User

class LoginForm (FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField ('Войти')

class RegistrationForm (FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Принять')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Пользователь с таким имененем уже существует')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Такой email уже зарегистрирован')

class EditProfileForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    about_me = TextAreaField('Расскажите о себе', validators=[Length(min=0, max=140)])
    submit = SubmitField('Принять')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Пользователь с таким именем уже существует')

class SetUserRatingForm(FlaskForm):
    title = StringField()
    year = IntegerField()
    genres = StringField()
    avgRating = FloatField()
    userRating = IntegerField(validators=[NumberRange(min=1, max=10)])
    userId = IntegerField()
    submit = SubmitField('Принять')