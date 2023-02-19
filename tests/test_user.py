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

        self.assertTrue(self.user1.validate_account_confirmation_token(self.user1.generate_user_token()))
        print(f'user1 token generation and validation is {True}')

        self.assertFalse(self.user1.validate_account_confirmation_token(self.user2.generate_user_token()))
        print(f'user1 token validation from user2 generated token is {False}')

        self.assertTrue(self.user1.confirmed)
        print(f'user1.confirmed is {True}')

        self.assertFalse(self.user2.confirmed)
        print(f'user2.confirmed is {False}')

    def test_password_reset(self):
        from app.models import User
        reset_token = self.user1.generate_user_token()
        self.assertTrue(self.user1.reset_password(reset_token, '858585'))
        del self.user1
        self.user1 = User.query.filter_by(email='johnny@example.com').first()
        self.assertTrue(self.user1.verify_password('858585'))

    def test_email_update_token(self):
        from app.models import User
        new_mail = 'johnny_newMail@example.com'
        token = self.user1.generate_email_update_token(new_email=new_mail)
        self.assertTrue(self.user1.update_email_by_token(token=token))
        self.assertEqual(self.user1.email, new_mail)
        self.assertIsNotNone(User.load_user_by_token(token))
        self.assertEqual(User.load_user_by_token(token).email, new_mail)
        self.assertIsNotNone(User.load_user_by_email(new_mail))
        self.assertEqual(User.load_user_by_email(new_mail).id, self.user1.id)
