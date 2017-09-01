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
        g_token=s.dumps({'confirm_id': 1,'rpasswd_email':'test1'})
        u1=User(id=1,email='test1')        
        u_token=u1.generate_token()
        self.assertTrue(g_token==u_token)

    def test_confirm_token(self):
        u2=User(id=2,email='test2')
        g_token=u2.generate_token()   
        self.assertTrue(u2.confirm(g_token))

    def test_rpasswd_token(self):
        u3=User(id=3,email='test3')       
        g_token=u3.generate_token()        
        self.assertTrue(u3.reset_passwd(g_token,'test'))