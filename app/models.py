from . import db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, AnonymousUserMixin
import jwt
from datetime import datetime, timedelta
import flasky
from flask import current_app

TOKEN_ID_KEY = 'user_id'
TOKEN_EXP_KEY = 'exp'
TOKEN_EMAIL_KEY = 'email'
ADMIN_ROLE_NAME = 'Administrator'
MODERATOR_ROLE_NAME = 'Moderator'
USER_ROLE_NAME = 'User'


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __init__(self, **kwargs):
        super(User, self).__init__(kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name=ADMIN_ROLE_NAME).first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return f'<User ({self.id}, {self.username})>'

    @property
    def password(self):
        raise AttributeError('user password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def load_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def load_user_by_token(token):
        raw_token = decode_token(token)
        id = raw_token[TOKEN_ID_KEY]
        return load_user(id)

    def can(self, permission):
        return self.role.has_permission(permission)

    def is_admin(self):
        return self.role.has_permission(Permission.ADMIN)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_user_token(self, expiration=3600):
        raw_token = dict()
        raw_token[TOKEN_EXP_KEY] = datetime.now() + timedelta(milliseconds=expiration)
        raw_token[TOKEN_ID_KEY] = self.id
        return encode_token(raw_token)

    def generate_email_update_token(self, new_email, expiration=3600):
        raw_token = dict()
        raw_token[TOKEN_EXP_KEY] = datetime.now() + timedelta(milliseconds=expiration)
        raw_token[TOKEN_ID_KEY] = self.id
        raw_token[TOKEN_EMAIL_KEY] = new_email
        return encode_token(raw_token)

    def update_email_by_token(self, token):
        try:
            raw_token = decode_token(token)
            if self.id == raw_token[TOKEN_ID_KEY]:
                self.email = raw_token[TOKEN_EMAIL_KEY]
                db.session.add(self)
                db.session.commit()
                return True
            else:
                return False
        except BaseException:
            return False

    def reset_password(self, token, new_password):
        try:
            raw_token = decode_token(token)
            if self.id == raw_token[TOKEN_ID_KEY]:
                return self.update_password(new_password)
            else:
                return False
        except BaseException:
            return False

    def update_password(self, new_password):
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def validate_account_confirmation_token(self, token):

        try:
            raw_token = decode_token(token)
        except BaseException:
            return False
        if raw_token.get(TOKEN_ID_KEY) != self.id:
            return False
        else:
            self.confirmed = True
            db.session.add(self)
            db.session.commit()
            return True


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
    default = db.Column(db.Integer, default=False, index=True)
    permissions = db.Column(db.Integer)

    def __init__(self, **kwargs):
        super(Role, self).__init__(kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        return f'<Role ({self.id},{self.name})>'

    @staticmethod
    def insert_roles():
        roles = {
            USER_ROLE_NAME: [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            MODERATOR_ROLE_NAME: [Permission.FOLLOW, Permission.COMMENT,
                                  Permission.WRITE, Permission.MODERATE],
            ADMIN_ROLE_NAME: [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }

        default_role = USER_ROLE_NAME
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions = self.permissions + perm
            return True
        else:
            return False

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions = self.permissions - perm
            return True
        else:
            return False

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


"""
Functions
"""


@login_manager.user_loader
def load_user(id):
    """
    used by flask_login for retrieving users by id

    :param id: identifier of the user in db
    :return: user object or None if identifier is wrong or any other error occured
    """
    return User.query.get(int(id))


def encode_token(raw_token):
    app = flasky.app
    return jwt.encode(payload=raw_token, key=app.config['SECRET_KEY'],
                      algorithm=app.config['CUSTOM_ENCRYPTION_ALGO'])


def decode_token(token):
    app = flasky.app
    return jwt.decode(jwt=token, key=app.config['SECRET_KEY'],
                      algorithms=app.config['CUSTOM_ENCRYPTION_ALGO'])
