from . import db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)

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

