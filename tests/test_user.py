from unittest import TestCase
from app import create_app, db


class test_user(TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        from app.models import User
        self.user1 = User(username='johnny', password='depp', email='johnny@example.com')
        self.user2 = User(username='jim', password='carrey', email='jim@example.com')
        db.session.add(self.user1)
        db.session.add(self.user2)
        db.session.commit()

    def tearDown(self):
        db.session.delete(self.user1)
        db.session.delete(self.user2)
        db.session.commit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_token(self):
        self.assertFalse(self.user1.confirmed)
        print(f'user1.confirmed is {False}')

        self.assertFalse(self.user2.confirmed)
        print(f'user2.confirmed is {False}')

        self.assertTrue(self.user1.validate_token(self.user1.generate_confirmation_token()))
        print(f'user1 token generation and validation is {True}')

        self.assertFalse(self.user1.validate_token(self.user2.generate_confirmation_token()))
        print(f'user1 token validation from user2 generated token is {False}')

        self.assertTrue(self.user1.confirmed)
        print(f'user1.confirmed is {True}')

        self.assertFalse(self.user2.confirmed)
        print(f'user2.confirmed is {False}')
