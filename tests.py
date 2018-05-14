from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, Post

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=retro&s=128'))

    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        f1 = Post(title="filmec1", liked=u1, userRating=7,
                  timestamp=now + timedelta(seconds=1))
        f2 = Post(title="filmec2", liked=u2, userRating=8,
                  timestamp=now + timedelta(seconds=4))
        f3 = Post(title="filmec3", liked=u3, userRating=9,
                  timestamp=now + timedelta(seconds=3))
        f4 = Post(title="filmec4", liked=u4, userRating=10,
                  timestamp=now + timedelta(seconds=2))
        db.session.add_all([f1, f2, f3, f4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        fo1 = u1.followed_posts().all()
        fo2 = u2.followed_posts().all()
        fo3 = u3.followed_posts().all()
        fo4 = u4.followed_posts().all()
        self.assertEqual(fo1, [f2, f4, f1])
        self.assertEqual(fo2, [f2, f3])
        self.assertEqual(fo3, [f3, f4])
        self.assertEqual(fo4, [f4])

if __name__ == '__main__':
    unittest.main(verbosity=2)