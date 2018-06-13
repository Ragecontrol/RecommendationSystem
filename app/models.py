from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login, app
from flask_login import UserMixin
from hashlib import md5
from time import time
import jwt


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

# user_film = db.Table('user_film',
#                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#                       db.Column('film_id', db.Integer, db.ForeignKey('film.id')),
#                       db.Column('userRating', db.Integer)
#                       )

class User_Film (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(64))
    film_id = db.Column(db.Integer)
    title = db.Column(db.String(255))
    user_rating = db.Column(db.Integer)

    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


class User (UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    # liked_films = db.relationship (
    #     'Film', secondary=user_film,
    #     backref=db.backref('users', lazy='dynamic'))



    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=retro&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_users(self):
        # followed = User_Film.query.join(
        #     followers, (followers.c.followed_id == User_Film.user_id)).filter(
        #     followers.c.followed_id == self.id, User_Film.user_rating !=0 )
        # own = User_Film.query.filter(User_Film.user_rating != 0, User_Film.user_id == self.id)
        #
        # return followed.union(own).order_by(User_Film.timestamp.desc())
        followed = User_Film.query.join(
            followers, (followers.c.followed_id == User_Film.user_id)).filter(
            followers.c.follower_id == self.id, User_Film.user_rating != 0)
        own = User_Film.query.filter(User_Film.user_rating !=0, User_Film.user_id == self.id)
        return followed.union(own).order_by(User_Film.timestamp.desc())
        # return User_Film.query.join(
        #     followers, (followers.c.followed_id == User_Film.user_id)).filter(
        #     followers.c.follower_id == self.id, User_Film.user_rating != 0).order_by(
        #     User_Film.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                algorithms=['HS256'])['reset_password']
        except:
              return
        return User.query.get(id)

    # def set_rating(self, film):
    #     self.liked_films.append(film)

    # def followed_posts(self):
    #     followed = Post.query.join(
    #         followers, (followers.c.followed_id == Post.user_id)).filter(
    #         followers.c.follower_id == self.id)
    #     own = Post.query.filter_by(user_id=self.id)
    #     return followed.union(own).order_by(Post.timestamp.desc())

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# class Post (db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(255))
#     year = db.Column(db.Integer, index=True)
#     genres = db.Column(db.String(255))
#     userRating = db.Column(db.Integer, index=True)
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#
#     def __repr__(self):
#         return '<Post {}>'.format(self.title)

class Film (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titleId = db.Column(db.String(64))
    title = db.Column(db.String(255))
    year = db.Column(db.String)
    genres = db.Column(db.String(255))


    def __init__(self,id, titleId, title, year, genres):
        self.id = id
        self.titleId = titleId
        self.title = title
        self.year = year
        self.genres = genres
