from . import db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
import jwt
from datetime import datetime, timedelta
import flasky


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    confirmed = db.Column(db.Boolean, default=False)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return f'<User ({self.id}, {self.username})>'

    @property
    def password(self):
        raise AttributeError('user password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        app = flasky.app
        raw_token = dict()
        raw_token['exp'] = datetime.now() + timedelta(milliseconds=expiration)
        raw_token['confirm'] = self.id
        return jwt.encode(payload=raw_token, key=app.config['SECRET_KEY'],
                          algorithm=app.config['CUSTOM_ENCRYPTION_ALGO'])

    def validate_token(self, token):
        app = flasky.app
        try:
            raw_token = jwt.decode(jwt=token, key=app.config['SECRET_KEY'], algorithms=app.config['CUSTOM_ENCRYPTION_ALGO'])
        except:
            return False
        if raw_token.get('confirm') != self.id:
            return False
        else:
            self.confirmed = True
            db.session.add(self)
            return True


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role ({self.id},{self.name})>'


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

