from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db, login
from flask_login import UserMixin

class User (UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    film = db.relationship('Film', backref='liked', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Film (db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(255))
        year = db.Column(db.DateTime, index=True)
        genres = db.Column(db.String(255))
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

        def __repr__(self):
            return '<Film {}>'.format(self.title)