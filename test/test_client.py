# -*- coding: utf-8 -*-
import unittest
from app import create_app,db
from app.models import User,Role
from flask import url_for
import re
class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app=create_app('testing')
        self.app_context=self.app.app_context()
        self.app_context.push()        
        db.create_all()
        Role.insert_roles()
        self.client=self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response=self.client.get(url_for('main.index'))
        self.assertTrue('Stranger' in response.get_data(as_text=True))

    def test_register_and_login(self):
        response=self.client.post(url_for('auth.register'),data={
            'email':'huu@huu.com',
            'username':'huu',
            'password':'cat',
            'password2':'cat'
            })
        self.assertTrue(response.status_code==302)

        response=self.client.post(url_for('auth.login'),data={
            'email':'huu@huu.com',
            'password':'cat'
            },follow_redirects=True)
        data=response.get_data(as_text=True)
        
        self.assertTrue(re.search(r'Hello,\s+huu',data))
        self.assertTrue('您还没有验证邮箱！检查您的邮箱，您应该已经收到了一份带有验证链接的邮件。' in data)

        user=User.query.filter_by(email='huu@huu.com').first()
        token=user.generate_token()
        response=self.client.get(url_for('auth.confirm',token=token),follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertTrue('邮箱验证成功！感谢' in data)

        response=self.client.get(url_for('auth.logout'),follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertTrue('你已经退出登录！' in data)