"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, connect_db
from sqlalchemy.exc import IntegrityError

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
    """ Test cases for the user model. """

    def setUp(self):
        """ Set up for user model tests. """

        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        u1.following.append(u2) # better to do in the test - more explicit

        db.session.commit()
        self.u1 = u1
        self.u2 = u2
        self.u1_id = u1.id
        self.u2_id = u2.id
        self.username = u1.username
        self.password = 'password'

        self.client = app.test_client()


    def tearDown(self):
        """ Tear down for user models tests. """        

        db.session.rollback()
        

    def test_user_model(self):
        """ Test if new user has no messages or followers. """

        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)


    def test_is_following(self):
        """ Tests if the User.is_following instance method works. """

        # test for method returning True - u1 DOES follow u2
        self.assertTrue(self.u1.is_following(self.u2))
        # test for method returning False - u2 DOES NOT follow u1
        self.assertFalse(self.u2.is_following(self.u1))


    def test_is_followed_by(self):
        """ Tests if the User.is_followed_by instance method works. """

        # test for method returning True - u2 IS followed by u1
        self.assertTrue(self.u2.is_followed_by(self.u1))
        # test for method returning False - u1 IS NOT followed by u2
        self.assertFalse(self.u1.is_followed_by(self.u2))


    def test_user_signup(self):
        """ Tests if the User.signup class method works. """

        u3 = User.signup("u3", "u3@email.com", "password", None)
        db.session.commit()
        self.assertIsNotNone(User.query.get(u3.id))
        # can test inidividual inputs are what make it into the database
        # can test that the password was successfully hashed
            # test for "$2b$" at start of password


    def test_unsuccessful_signup(self):
        """ Test for failed sign up, due to missing 
        input or duplicate username """

        u3 = User.signup("u3", "u3@email.com", "password", None)
        db.session.commit()

        # test for unsuccessful signup, due to missing required input
        with self.assertRaises(IntegrityError):
            User.signup(None, "u4@email.com", "password", None)
            db.session.commit()

        db.session.rollback()

        # test for unsuccessful signup, due to duplicate username
        with self.assertRaises(IntegrityError):
            User.signup("u3", "u5@email.com", "password", None)
            db.session.commit()


    def test_authenticate(self):
        """ Test the class method authenticate. """

        # Test correct username, password
        self.assertTrue(User.authenticate(self.username, self.password))
        # could also make sure that a successful authentication returns the
        # correct user - right now, could be getting back a different user
        # somehow...

        # Test incorrect password
        self.assertFalse(User.authenticate(self.username, 'cupcake'))
        # Test incorrect username
        self.assertFalse(User.authenticate('fake', self.password))
