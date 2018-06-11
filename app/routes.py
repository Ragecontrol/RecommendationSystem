from flask import render_template, flash, redirect, url_for, request
from app import app,db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Film, User_Film
from werkzeug.urls import url_parse
from sqlalchemy import and_, exists
from app.email import send_password_reset_email
import sqlite3
from scipy.sparse import lil_matrix, spdiags, vstack
from sklearn.preprocessing import normalize
import numpy as np

@app.route('/')
@app.route('/index')
def index():

    return render_template('index.html', title='Главная')

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
        user_table_check = User.query.filter_by(username=form.username.data).first()
        user_ch = User_Film.query.filter_by(user_id=user_table_check.id, username=user_table_check.username).first()
        if user_ch is None:
            films = Film.query.all()
            for f in films:
                user_r = User_Film(user_id=user_table_check.id, username=user_table_check.username, film_id=f.id, title=f.title)
                db.session.add(user_r)
            db.session.commit()
        flash('Регистрация прошла успешно')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = User_Film.query.filter(User_Film.user_rating != 0, User_Film.username == username).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html',title=username, user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.set_password(form.password.data)
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
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    users_sql = """
            SELECT user_id
            FROM user__film
            WHERE user_rating IS NOT NULL
            GROUP BY user_id HAVING count(film_id) >= 2
        """
    cursor.execute(users_sql)
    user_to_col = {}
    for col_id, (user_id,) in enumerate(cursor):
        user_to_col[user_id] = col_id

    objs_sql = """
            SELECT film_id
            FROM user__film
            WHERE user_rating IS NOT NULL AND user_id IN (
                SELECT user_id
                FROM user__film
                WHERE user_rating IS NOT NULL
                GROUP BY user_id HAVING count(film_id) >= 2
            )
            GROUP BY film_id HAVING count(user_id) >= 1
        """
    cursor.execute(objs_sql)
    obj_to_row = {}
    for row_id, (obj_id,) in enumerate(cursor):
        obj_to_row[obj_id] = row_id

    sql = """
            SELECT film_id, user_id, user_rating
            FROM user__film
            WHERE user_rating IS NOT NULL
        """
    cursor.execute(sql)

    matrix = lil_matrix((len(obj_to_row), len(user_to_col)))

    for obj_id, user_id, rate in cursor:
        row_id = obj_to_row.get(obj_id)
        col_id = user_to_col.get(user_id)
        if row_id is not None and col_id is not None:
            matrix[row_id, col_id] = min(rate, 10)

    normalized_matrix = normalize(matrix.tocsr()).tocsr()
    cosine_sim_matrix = normalized_matrix.dot(normalized_matrix.T)
    diag = spdiags(-cosine_sim_matrix.diagonal(), [0], *cosine_sim_matrix.shape, format='csr')
    cosine_sim_matrix = cosine_sim_matrix + diag
    cosine_sim_matrix = cosine_sim_matrix.tocsr()
    m = 14

    rows = []
    for row_id in np.unique(cosine_sim_matrix.nonzero()[0]):
        row = cosine_sim_matrix[row_id]
        if row.nnz > m:
            work_row = row.tolil()

            work_row[0, row.nonzero()[1][np.argsort(row.data)[-m:]]] = 0
            row = row - work_row.tocsr()
        rows.append(row)
    topk_matrix = vstack(rows)
    topk_matrix = normalize(topk_matrix)

    row_to_obj = {row_id: obj_id for obj_id, row_id in obj_to_row.items()}

    title_sql = """
            SELECT film_id, title
            FROM user__film
            GROUP BY film_id, title
        """
    cursor.execute(title_sql)
    obj_to_title = {}
    for obj_id, title in cursor:
        obj_to_title[obj_id] = title

    cursor.execute(
        "SELECT user_id FROM user__film WHERE user_id = ? AND user_rating IS NOT NULL GROUP BY user_id HAVING count(film_id) >= 2",
        (current_user.id,))
    cur_user_to_col = {}
    for col_id, (user_id,) in enumerate(cursor):
        cur_user_to_col[user_id] = col_id

    user_vector = lil_matrix((len(obj_to_row), 1))

    cursor.execute(sql)

    for obj_id, user_id, rate in cursor:
        row_id = obj_to_row.get(obj_id)
        col_id = cur_user_to_col.get(user_id)
        if row_id is not None and col_id is not None:
            user_vector[row_id, col_id] = min(rate, 10)

    user_vector = user_vector.tocsr()
    x = topk_matrix.dot(user_vector).tolil()
    for i, j in zip(*user_vector.nonzero()):
        x[i, j] = 0

    x = x.T.tocsr()

    quorum = 12
    data_ids = np.argsort(x.data)[-quorum:][::-1]

    result = []
    for arg_id in data_ids:
        row_id, p = x.indices[arg_id], x.data[arg_id]
        obj_id = row_to_obj[row_id]

        impact_vector = topk_matrix[row_id].multiply(user_vector.T)

        impacted_arg_id = np.argsort(impact_vector.data)[-1]
        impacted_row_id = impact_vector.indices[impacted_arg_id]
        impact_value = user_vector[impacted_row_id, 0]
        impacted_obj_id = row_to_obj[impacted_row_id]

        rec_item = {
            "title": obj_to_title[obj_id],
            "weight": p,
            "impact": obj_to_title[impacted_obj_id],
            "impact_value": impact_value
        }
        result.append(rec_item)


    cursor.execute("SELECT film_id FROM user__film WHERE user_rating >=7 AND user_id IN (SELECT user_id FROM user__film WHERE user_rating IS NOT NULL GROUP BY user_id HAVING count(film_id) >= 2) GROUP BY film_id HAVING count(user_id) >= 2")

    pop_obj_to_row = {}
    for row_id, (obj_id,) in enumerate(cursor):
        pop_obj_to_row[obj_id] = row_id

    pop_matrix = lil_matrix((len(pop_obj_to_row), len(user_to_col)))

    cursor.execute("SELECT film_id, user_id, user_rating FROM user__film WHERE user_rating >=7")

    for obj_id, user_id, rate in cursor:
        row_id = pop_obj_to_row.get(obj_id)
        col_id = user_to_col.get(user_id)
        if row_id is not None and col_id is not None:
            pop_matrix[row_id, col_id] = min(rate, 10)



    pop_matrix = pop_matrix.T.tocsr()
    pop_films = []
    pop_data_ids=np.argsort(pop_matrix.data)[-quorum:][::-1]

    for arg_id in pop_data_ids:
        row_id, p = pop_matrix.indices[arg_id], pop_matrix.data[arg_id]
        obj_id = row_to_obj[row_id]

        rec_item = {
            "title": obj_to_title[obj_id],

        }
        pop_films.append(rec_item)

    page = request.args.get('page', 1, type=int)

    q= request.args.get('q')
    if q:
        items = db.session.query(Film).filter(and_(Film.title.contains(q), Film.year >= '1900', Film.year <= '2018')).order_by(Film.year.desc())
    else:
        items = db.session.query(Film).filter(and_(Film.year >= '1900', Film.year <= '2018')).order_by(Film.year.desc()).paginate(page, app.config['FILM_PER_PAGE'], False)
        next_url = url_for('films', page=items.next_num) \
            if items.has_next else None
        prev_url = url_for ('films', page=items.prev_num)   \
            if items.has_prev else None
        return render_template('/films.html', title='Фильмы', items=items.items, next_url=next_url, prev_url=prev_url,
                               result=result, pop_films=pop_films)
    return render_template('/films.html', title='Фильмы', items=items, result=result, pop_films=pop_films)

@app.route('/saveStars/<countStar>/<idItem>/<title>')
@login_required
def saveStar(countStar,idItem,title):
    user_id = current_user.id
    film_id = idItem
    user_rating = countStar
    title = title
    rating = User_Film.query.filter_by(user_id=user_id, film_id=film_id).first()
    if rating is None:
        rating = User_Film (user_id=user_id,username=current_user.username, film_id=film_id, title=title, user_rating=user_rating)
        db.session.add(rating)
    else:
        User_Film.query.filter_by(user_id=user_id, film_id=film_id, title=title).update({'user_rating': user_rating})
    db.session.commit()
    print(str(user_rating) + str(user_id) + str(film_id))

    return redirect(url_for('films'))

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Проверьте ваш email для получения дальнейших инструкций')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Сброс пароля', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Пароль изменен')
        return redirect(url_for('login'))
    return render_template('reset_password.html',title='Смена пароля', form=form)

@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = User_Film.query.filter(User_Film.user_rating != 0).order_by(User_Film.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('news.html', title='Оценки пользователей', posts=posts.items, next_url=next_url, prev_url=prev_url)

@app.route('/news')
@login_required
def news():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_users().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('news.html', title='Новости',posts=posts.items, next_url=next_url, prev_url=prev_url)

