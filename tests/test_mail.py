import unittest
from app import create_app, db
from app import mail, email
from app import models


class MailModuleTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user1 = models.User(username='test_user_1', password='1234',email='navid.me@mtnirancell.com')
        db.session.add(self.user1)
        db.session.commit()

    def tearDown(self):
        db.session.delete(self.user1)
        db.session.commit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_mail(self):
        mail_thread = email.send_mail('navid.me@mtnirancell.ir',
                                      'test case // email test scenario',
                                      body='mail sent from python test scenarios')

        self.assertTrue(mail_thread, not None)

    def test_mail_v2(self):
        to = list()
        to.append(self.user1.email)
        subject = f'Please confirm your account'
        template = f'auth/email/confirmation_email'
        mail_thread = email.send_mail_v2(to=to, subject=subject, template=template, user=self.user1,
                                         token=self.user1.generate_user_token())

        self.assertTrue(mail_thread, not None)

