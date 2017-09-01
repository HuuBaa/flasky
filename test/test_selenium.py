# -*- coding: utf-8 -*-
from selenium import webdriver
import unittest
from app import create_app,db
from app.models import User,Role,Post
from flask import url_for
import threading
import re
import time
class SeleniumTestCase(unittest.TestCase):
    client=None

    @classmethod
    def setUpClass(cls):
        try:
            cls.client=webdriver.Firefox()
        except BaseException as e:
            print(e)

        if cls.client:
            cls.app=create_app('testing')
            cls.app_context=cls.app.app_context()
            cls.app_context.push()

            import logging
            logger=logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            admin_role=Role.query.filter_by(permissions=0xff).first()
            admin = User(email='huu@example.com',username='huu', password='cat',role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            threading.Thread(target=cls.app.run).start()
            time.sleep(1) 


    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()

            db.drop_all()
            db.session.remove()

            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        self.client.get('http://localhost:5000')
        self.assertTrue(re.search(r'Hello,\s+Stranger!',self.client.page_source))

        self.client.find_element_by_link_text('登录').click()
        self.assertTrue('<h1>Login</h1>' in self.client.page_source)

        self.client.find_element_by_name('email').send_keys('huu@example.com')
        self.client.find_element_by_name('password').send_keys('cat')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search(r'Hello,\s+huu!', self.client.page_source))

        self.client.find_element_by_link_text('用户资料').click()
        self.assertTrue('<h1>huu</h1>' in self.client.page_source)
