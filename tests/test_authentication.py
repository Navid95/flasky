import unittest
import app.models as m
from app import db, create_app


class AuthenticationTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hash_not_equal(self):
        u1 = m.User()
        u2 = m.User()

        u1.password = 'cat'
        u2.password = 'cat'

        self.assertNotEqual(u1.password_hash, u2.password_hash)

    def test_password_not_readable(self):
        u = m.User()
        u.password = '1234'
        u.username = 'hi'
        with self.assertRaises(AttributeError):
            print(f'User password is: {u.password}')

    def test_verify_password(self):
        u1 = m.User()
        u1.password = 'dog'
        self.assertTrue(u1.password_hash is not None)
        self.assertTrue(u1.verify_password('dog'))

