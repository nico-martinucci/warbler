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

class MessageModelTestCase(TestCase):
    def setUp(self):
        """ Set up for message model tests. """

        Message.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        db.session.flush()

        m1 = Message(text="test message")
        u1.messages.append(m1)

        db.session.commit()

        self.u1 = u1
        self.m1 = m1
        self.m1_id = m1.id

        self.client = app.test_client()


    def tearDown(self):
        """ Tear down for message model tests. """

        db.session.rollback()

    
    def test_create_new_message(self):
        """ Test successfully creating a new message. """

        m2 = Message(text="test message 2")
        self.u1.messages.append(m2)

        db.session.add(m2)
        db.session.commit()

        self.assertIsNotNone(Message.query.get(m2.id))
        self.assertEqual(m2.user.username, "u1")
        # more detail - could test that title=title, text=text, etc.

    
    def test_create_duplicate_message(self):
        """ Test successfully creating a duplicate message - should work! """

        m2 = Message(text="test message")
        self.u1.messages.append(m2)

        db.session.add(m2)
        db.session.commit()

        self.assertIsNotNone(Message.query.get(m2.id))
        self.assertEqual(len(self.u1.messages), 2)
        # for more detailed (incl. user), do the query with filtering above


    def test_create_empty_message(self):
        """ Test trying to create a message with no text - should fail! """

        with self.assertRaises(IntegrityError):
            m2 = Message(text=None)
            self.u1.messages.append(m2)

            db.session.add(m2)
            db.session.commit()


    def test_delete_user_message_cascade(self):
        """ Test deleting user, making sure messages get deleted too. """

        User.query.delete()
        db.session.commit()

        self.assertIsNone(Message.query.get(self.m1_id))
