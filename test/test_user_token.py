import unittest
from app.models import User
from flask import current_app
from app import create_app,db
from itsdangerous import TimedJSONWebSignatureSerializer  as Serializer
class UserConfirmTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_generate_token(self):
        s=Serializer(current_app.config['SECRET_KEY'],expires_in=3600)
        g_token=s.dumps({'confirm_id': 23,'rpasswd_email':'test'})
        u_token=User(id=23,email='test').generate_token()
        self.assertTrue(g_token==u_token)

    def test_confirm_token(self):
        s=Serializer(current_app.config['SECRET_KEY'],expires_in=3600)
        g_token=s.dumps({'confirm_id': 23,'rpasswd_email':'test'})       
        self.assertTrue(User(id=23,email='test').confirm(g_token))

    def test_rpasswd_token(self):
        s=Serializer(current_app.config['SECRET_KEY'],expires_in=3600)
        g_token=s.dumps({'confirm_id': 23,'rpasswd_email':'test'})       
        self.assertTrue(User(id=23,email='test').reset_passwd(g_token,'test'))