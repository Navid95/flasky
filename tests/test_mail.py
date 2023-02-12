import unittest
from app import create_app, db
from app import mail, email


class mail_module_test_case(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_mail(self):
        mail_thread = email.send_mail('navid.me@mtnirancell.ir',
                                        'test case // email test scenario',
                                        'mail sent from python test scenarios')

        self.assertTrue(mail_thread, not None)

