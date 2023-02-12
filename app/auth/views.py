from . import auth
from flask import render_template, request


@auth.route('/login')
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    print(f'username: {username}\npassword: {password}')
    print(f'request: {request}')
    return render_template('auth/login.html')
