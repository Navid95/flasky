from . import auth, forms
from flask import render_template, request, url_for, redirect, flash
from ..models import User
from flask_login import login_user, logout_user, login_required
from flasky import db



@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Validations by priority:
        - validates form data
        - gets user from DB by email address
        - checks if user is not None & verifies password
            - logs user in
            - checks if user was redirected from a url which needs authentication
                - if True redirects to origin url
                - if False redirects to main.index
        - informs user that credentials were wrong
        - returns to login page with from data
    :return: main / login / user's origin url
    """
    form = forms.LoginForm()
    if form.validate_on_submit():
        print(f'Form validated')
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            print(f'User not None and password is verified')
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                print(f'User was not redirected for login from another route.')
                next = url_for('main.init')
            return redirect(next)
        else:
            flash('Invalid username/password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f'You have been logged out.')
    return redirect(url_for('main.init'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    password=form.password.data,
                    email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash(message='You can now login')
        return redirect(url_for('auth.login'))
    else:
        return render_template('auth/register.html', form=form)
