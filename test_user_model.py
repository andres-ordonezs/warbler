"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError


from models import db, User, Message, Follow

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_is_following_true(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.following.append(u2)

        self.assertEqual(u1.is_following(u2), True)

    def test_is_following_false(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(u1.is_following(u2), False)

    def test_is_followed_by_true(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        u1.followers.append(u2)

        self.assertEqual(u1.is_followed_by(u2), True)

    def test_is_followed_by_false(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(u1.is_followed_by(u2), False)

    def test_user_signup_valid(self):
        u3 = User.signup("u3", "u3@email.com", "password", None)

        self.assertIsInstance(u3, User)

    def test_user_signup_invalid(self):
        with self.assertRaises(IntegrityError):
            User.signup("u1", "u3@email.com", "password", None)
            db.session.commit()

    def test_authenticate_valid(self):
        result = User.authenticate("u1", "password")

        self.assertEqual(result.id, self.u1_id)

    def test_authenticate_username_invalid(self):
        result = User.authenticate("u3", "password")

        self.assertEqual(result, False)

    def test_authenticate_password_invalid(self):
        result = User.authenticate("u1", "pass")

        self.assertEqual(result, False)