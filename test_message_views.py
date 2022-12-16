"""Message View tests."""

# run these tests like:
#
#    FLASK_DEBUG=False python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Message, User, Like, connect_db

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# This is a bit of hack, but don't use Flask DebugToolbar

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

connect_db(app)

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False



class MessageViewsTestCase(TestCase):
    """ Test cases for views related to messages. """

    def setUp(self):
        """ Set up for message view tests. """

        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)

        db.session.commit()

        self.u1_id = u1.id
        self.u1 = u1

        self.client = app.test_client()
    

    def tearDown(self):
        """ Tear down for message view tests. """

        db.session.rollback()
    

    def test_get_add_message(self):
        """ Test route to add message landing page. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1_id
            resp = c.get(f'/messages/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test add message", html)


    def test_post_message(self):
        """ Test route to post new message. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1_id
            data = {
                'text': "new post!"
            }

            resp = c.post('/messages/new', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test show user detial", html)
            self.assertIn("new post!", html)


    def test_get_show_message(self):
        """ Test route to show message landing page. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1_id

            test_msg = Message(text="test message")
            self.u1.messages.append(test_msg)
            db.session.commit()

            resp = c.get(f'/messages/{self.u1.messages[0].id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test message", html)


    def test_delete_message(self):
        """ Test route to delete a message.  """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1_id

            test_msg = Message(text="test message")
            self.u1.messages.append(test_msg)
            db.session.commit()

            resp = c.post(
                f'/messages/{test_msg.id}/delete',
                follow_redirects=True
            )
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("test message", html)


    def test_like_message(self):
        """ Test route to like a message. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1_id

            test_msg = Message(text="test message")
            self.u1.messages.append(test_msg)
            db.session.commit()

            data = {
                'redirect_loc': "/",
                'message_id': test_msg.id,
                'like': None
            }

            resp = c.post(f'/messages/likes', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test homepage", html)


    def test_unlike_message(self):
        """ Test route to like a message. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.u1_id

            test_msg = Message(text="test message")
            self.u1.messages.append(test_msg)
            db.session.commit()

            data = {
                'redirect_loc': "/",
                'message_id': test_msg.id,
                'like': Like.query.get((self.u1.id, test_msg.id))
            }

            resp = c.post(f'/messages/likes', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test homepage", html)