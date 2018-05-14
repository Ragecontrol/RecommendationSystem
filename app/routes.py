from flask import render_template, flash, redirect, url_for, request, json
from app import app,db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, SetUserRatingForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Film
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
    posts = [
        {'liked': user, 'title': 'filmec1', 'userRating': '8'},
        {'liked': user, 'title': 'filmec2', 'userRating': '9'},
    ]
    return render_template('user.html', user=user, posts=posts)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Редактирование профиля',
                           form=form)

@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Пользователь {} не найден.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('Нарциссизм - это плохо')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('Вы подписаны на {}'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Пользователь {} не найден.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('Сильно Вы себя, однако, не любите')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('Вы отписаны от {}'.format(username))
    return redirect(url_for('user', username=username))

@app.route('/films', methods=['GET', 'POST'])
@login_required
def films():
    # form = SetUserRatingForm()
    # if form.validate_on_submit():
    #     p = Post.query.filter_by(title=form.title.data).filter_by(liked=current_user).first()
    #     if p:
    #         p.userRating = form.userRating.data
    #     else:
    #         postF = Post(title=form.title.data, year=form.year.data, genres=form.genres.data,
    #                      userRating=form.userRating.data, liked=current_user)
    #         db.session.add(postF)
    #     db.session.commit()
    return render_template('/films.html', items=Film.query.all())

# @app.route('/films',methods=['GET', 'POST'])
# @login_required
# def post():
#     form = SetUserRatingForm()
#     if form.validate_on_submit():
#         p = Post.query.filter_by(title=form.title.data).filter_by(liked=current_user).first()
#         if p:
#             p.userRating=form.userRating.data
#         else:
#             postF = Post(title=form.title.data, year=form.year.data, genres=form.genres.data, userRating=form.userRating.data, liked=current_user)
#             db.session.add(postF)
#         db.session.commit()
#     return redirect(url_for('films'))


