"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, connect_db

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

connect_db(app)

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        u1.following.append(u2)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)


    def test_is_following(self):
        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertTrue(u1.is_following(u2))


# Does is_following successfully detect when user1 is following user2?
    # 2 users. 1 follows the other in db.
    # User1 follows user 2, but user 2 does not follow user 1.
# Does is_following successfully detect when user1 is not following user2?

# Does is_followed_by successfully detect when user1 is followed by user2?

# Does is_followed_by successfully detect when user1 is not followed by user2?

# Does User.signup successfully create a new user given valid credentials?

# Does User.signup fail to create a new user if any of the validations (eg uniqueness, non-nullable fields) fail?

# Does User.authenticate successfully return a user when given a valid username and password?

# Does User.authenticate fail to return a user when the username is invalid?

# Does User.authenticate fail to return a user when the password is invalid?