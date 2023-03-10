"""User view tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py
import os
from unittest import TestCase
from flask import session
from models import db, User, Message, Follows, connect_db, Like

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY, g

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

connect_db(app)

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False
# One method test per view function

class UserViewsTestCase(TestCase):
    """ Test cases for views related to users and user interaction. """

    def setUp(self):
        """ Set up for user view tests. """
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.flush()
        db.session.commit()

        self.u1 = u1
        self.u2 = u2
        self.username = u1.username
        self.password = "password"
        self.id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()


    def tearDown(self):
        """ Tear down for user view tests. """

        db.session.rollback()


    def test_get_signup(self):
        """ Test for get request to /signup end point. """

        with self.client as c:
            resp = c.get('/signup')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Join Warbler today.", html)


    def test_post_signup(self):
        """ Test for post request to /signup end point - redirects to /. """

        # test for good payloud to /signup
        with self.client as c:
            data = {
                'username': 'Greg',
                'password': 'badbob666',
                'email': 'greg@gmail.com',
                'image_url': "/static/images/default-pic.png"
            }

            resp = c.post('/signup', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test homepage", html)


    def test_bad_post_signup(self):
        """ Test for bad payloud to /signup - 
        repeat information. re-renders the page. """

        with self.client as c:
            data = {
                'username': 'u1',
                'password': 'u1_test@email.com',
                'email': 'password',
                'image_url': None
            }

            resp = c.post('/signup', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username already taken", html)


    def test_get_login(self):
        """ Test for get to login page at /login endpoint. """

        with self.client as c:
            resp = c.get('/login')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome back.", html)

    def test_post_login(self):
        """ Test for get to login page at /login endpoint. """

        # post to route with good paylod
        with self.client as c:
            data = {
                'username': self.username,
                'password': self.password
            }

            resp = c.post('/login', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test homepage", html)

        # post to route with bad paylod - incorrect password
        with self.client as c:
            data = {
                'username': self.username,
                'password': "BadPassword"
            }

            resp = c.post('/login', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Invalid credentials.", html)


    def test_logout(self):
        """ Test route for logging out current user. """

        with self.client as c:
            resp = c.post('/login', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome back.", html)


    def test_list_users(self):
        """ Test route for lising of users. """


        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            resp = c.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test user index", html)


    def test_show_user(self):
        """ Test route for lising of users. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            resp = c.get(f'/users/{self.id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test show user", html)


    def test_show_following(self):
        """ Test route for showing who the current user is following. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            resp = c.get(f'/users/{self.id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test show following", html)
        # could make users follow each other and check for their names

    def test_show_followers(self):
        """ Test route for showing who is following the current user. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            resp = c.get(f'/users/{self.id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test show followers", html)
        # could make users follow each other and check for their names


    def test_liked_messages(self):
        """ Test route for showing all liked messages. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id
                
            resp = c.get(f'/users/{self.id}/liked_messages')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test show liked messages", html)
        # more detail: test to make sure an actual liked message
        # is on the page


    def test_start_following(self):
        """ Test route for following other users. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            resp = c.post(f'/users/follow/{self.u2_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("u2", html)


    def test_stop_following(self):
        """ Test route to stop following other users. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            self.u1.following.append(self.u2)

            resp = c.post(f'/users/stop-following/{self.u2_id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("u2", html)


    def test_get_edit_profile(self):
        """ Test route to get edit profile page.  """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            resp = c.get(f'/users/profile')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test edit user", html)


    def test_post_edit_profile(self):
        """ Test route to edit profile """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            data = {
                'username': self.username,
                'password': self.password
            }

            resp = c.post(f'/users/profile', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test show user detial", html)
            # another opportunity to test more specific edits


    def test_delete_user(self):
        """ Test route to delete user. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            resp = c.post(f'/users/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test signup page", html)


    def test_homepage(self):
        """ Test route to show homepage. """

        with self.client as c:
            with c.session_transaction() as change_session:
                change_session[CURR_USER_KEY] = self.id

            resp = c.get(f'/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("test homepage", html)


    # test app.before_request & app.after_request routes?