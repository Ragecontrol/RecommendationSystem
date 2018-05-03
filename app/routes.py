from flask import render_template, flash, redirect, url_for, request
from app import app,db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Film
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Максим'}
    # Здесь будут последние записи из БД
    objects = [
        {
            'title': 'Криминально чтиво',
            'year': '1999',
            'genre': 'триллер',
            'rating': '7.8',
            'link': 'кримчтиво.ком'
        },
        {
            'title': 'Мстители',
            'year': '2012',
            'genre': 'фантастика',
            'rating': '8.0',
            'link': 'мстители.ком'
        },
        {
            'title': 'Тихоокеанский рубеж',
            'year': '2011',
            'genre': 'боевик',
            'rating': '6.9',
            'link': 'тихрубеж.ком'
        }
    ]
    return render_template('index.html', title='Главная', objects=objects)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверный логин/пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Авторизация', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user=User.query.filter_by(username=username).first_or_404()
    films = [
        {'liked': user, 'title': 'filmec1', 'userRating': '8'},
        {'liked': user, 'title': 'filmec2', 'userRating': '9'},
    ]
    return render_template('user.html', user=user, films=films)