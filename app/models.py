from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin
from hashlib import md5

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

user_film = db.Table('user_film',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('film_id', db.Integer, db.ForeignKey('film.id'))
                     )

class User (UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    post = db.relationship('Post', backref='liked', lazy='dynamic')
    about_me = db.Column(db.String(140))
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    liked_films = db.relationship(
        'User', secondary=user_film,
        primaryjoin=(user_film.c.user_id == id),
        secondaryjoin=(user_film.c.film_id==id),
        backref=db.backref('user_film', lazy='dynamic'), lazy='dynamic'
    )

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

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    year = db.Column(db.Integer, index=True)
    genres = db.Column(db.String(255))
    userRating = db.Column(db.Integer, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.title)

class Film (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titleId = db.Column(db.String, index=True)
    title = db.Column(db.String(255))
    year = db.Column(db.Integer)
    genres = db.Column(db.String(255))
    avgRating = db.Column(db.Float, index=True)

    def __init__(self, titleId, title, year, genres, avgRating):
        self.titleId = titleId
        self.title = title
        self.year = year
        self.genres = genres
        self.avgRating = avgRating