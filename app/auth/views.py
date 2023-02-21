from . import auth, forms
from flask import render_template, request, url_for, redirect, flash
# from ..models import User
import app.models as m
from flask_login import login_user, logout_user, login_required, current_user
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
        user = m.User.query.filter_by(email=form.email.data).first()
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
    from app import email as mail
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        user = m.User(username=form.username.data,
                    password=form.password.data,
                    email=form.email.data)
        db.session.add(user)
        db.session.commit()
        mail.send_registration_confirm_link(user)
        flash(message='You can now login')
        return redirect(url_for('auth.login'))
    else:
        return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>', methods=['GET'])
@login_required
def confirm(token):
    print(f'Received token for confirmation:\n{token}')
    if not current_user.confirmed:
        print(f'Current user os not confirmed')
        if current_user.validate_account_confirmation_token(token):
            flash('Account activated successfully.')
            print(f'Account activated successfully')
        else:
            flash('Confirmation link is not valid or is expired.')
            print(f'Confirmation link is not valid or is expired.')

    else:
        flash('User account is already activated')
        print('User account is already activated')
    return redirect(url_for('main.init'))


@auth.before_app_request
def before_app_request():
    print(f'{__name__}: before_app_request hook, headers: {request}, user: {current_user}')
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static' \
            and request.endpoint != 'main.init':
        print(f'{__name__}: User account {current_user} is not confirmed')
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed', methods=['GET'])
@login_required
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.init'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    from app import email as mail
    mail.send_registration_confirm_link(current_user)
    flash(f'A new confirmation link sent to {current_user.email}.')
    return redirect(url_for('main.init'))


@auth.route('/password/update', methods=['GET', 'POST'])
@login_required
def update_pass():
    form = forms.PasswordUpdateForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.password.data):
            if current_user.update_password(form.password.data):
                return redirect(url_for('main.init'))
            else:
                flash('An error occurred during the password update, please contact application support team.')
        else:
            flash('New password cannot be same as old password.')
    form.email.data = current_user.email
    form.username.data = current_user.username
    return render_template('auth/updatepass.html', form=form)


@auth.route('/password/reset', methods=['GET', 'POST'])
def reset_pass_generate():
    form = forms.PasswordResetRequest()
    if form.validate_on_submit():
        user = m.User.load_user_by_email(form.email.data)
        if user is not None:
            from app import email as mail
            mail.send_password_reset_link(user)
            return redirect(url_for('main.init'))
        else:
            flash(f'{form.email.data} does not correspond to any user account.')
    else:
        flash(f'Please make sure to fill the form correctly')
    return render_template('auth/resetpass.html', form=form)


@auth.route('/password/reset/<token>', methods=['GET', 'POST'])
def reset_pass(token):
    user = m.User.load_user_by_token(token)
    if user is not None:
        form = forms.PasswordUpdateForm()
        if form.validate_on_submit():
            if user.reset_password(token, form.password.data):
                flash('Password changed Successfully')
                return redirect(url_for('auth.login'))
            else:
                flash('Error in updating the password. Reset link might be corrupted, '
                      'if you are sure about your email address please request for another link')
                render_template('auth/updatepass.html', form=form)
        else:
            flash('Please make sure to fill the form completely')
            form.email.data = user.email
            form.username.data = user.username
            return render_template('auth/updatepass.html', form=form)
    else:
        flash('Could not find any user with the email address associated with the link. Reset link might be corrupted, '
              'if you are sure about your email address please request for another link')
        return redirect(url_for('auth.reset_pass_generate'))


@auth.route('/email/update', methods=['GET', 'POST'])
@login_required
def update_email_generate():
    form = forms.EmailUpdateRequest()
    if form.validate_on_submit():
        # TODO search if this is the correct way to avoid circular imports
        from app import email as mail
        mail.send_email_update_link(current_user, form.email2.data)
        return redirect(url_for('main.init'))
    else:
        flash('Please make sure to fill the form completely')
        form.email.data = current_user.email
        form.username.data = current_user.username
        return render_template('auth/updateemail.html', form=form)


@auth.route('/email/update/<token>', methods=['GET'])
@login_required
def update_email(token):
    print(f'{__name__}: current_user email={current_user.email}')
    if current_user.update_email_by_token(token):
        print(f'{__name__}: email address updated successfully')
        print(f'{__name__}: current_user email={current_user.email}')
        flash('Email address updated successfully')
        logout_user()
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('auth.update_email_generate'))


