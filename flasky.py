import os
from app import create_app, db
from flask_migrate import Migrate
import app.models as models

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)

print(f'App created with DB URI: {app.config["SQLALCHEMY_DATABASE_URI"]}')

with app.app_context():
    db.create_all()
    db.session.commit()
    print('db created')

print(app.config['MAIL_PASSWORD'])
print(app.config['MAIL_USERNAME'])


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=models.User, Role=models.Role, FLASK_APP='flasky.py')


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


