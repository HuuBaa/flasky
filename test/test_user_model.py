import unittest
from app.models import User,Role,Permission,AnonymousUser
from app import create_app,db
class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u=User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u=User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_verify_password(self):
        u=User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_has_random_salts(self):
        u=User(password='cat')
        u2=User(password='cat')
        self.assertFalse(u.password_hash == u2.password_hash)

    def test_roles_permission(self):
        u=User(email='1234@qq.com',password='test')
        self.assertTrue(u.can(Permission.WRITE_ARTICLES))
        self.assertFalse(u.can(Permission.MODERATE_COMMEMTS))

    def test_anonymous_user(self):
        u=AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))