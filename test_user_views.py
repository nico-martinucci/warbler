"""User view tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py
import os
from unittest import TestCase
from models import db, User, Message, Follows, connect_db

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

connect_db(app)

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False
# One method test per view function

class TestUserViews(TestCase):
    def setUp(self):
        self.client = app.test_client()


    def test_get_signup(self):
        with self.client as c:
            resp = c.get('/signup')
            html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("Join Warbler today.", html)

    def test_post_signup(self):
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

    # with app.test_client() as client:
    #         # test with one nonsense currency abbreviation
    #         data = {
    #             "converting-from": "GIBBERISH",
    #             "converting-to": "GBP",
    #             "converting-amount": "100"
    #         }
    #         response = client.post("/", data=data, follow_redirects=True)
    #         html = response.get_data(as_text=True)

    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn("<!--TESTCHECK: home page, index.html-->", html)
    #         self.assertIn("Not a valid code: ", html)
