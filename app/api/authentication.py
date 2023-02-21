from flask_httpauth import HTTPBasicAuth
import app.models as m
from flask import g, jsonify, abort, request, session
from app.api import api
from .errors import forbidden

auth = HTTPBasicAuth()

"""
AUTH Token key/vals
"""
AUTH_TOKEN_KEY = 'token'
AUTH_TOKEN_EXP_KEY = 'exp'
AUTH_TOKEN_EXP_VAL = 3600


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return False
    elif password != '':
        # user = m.User.query.filter_by(email=email_or_token).first()
        user = m.User.load_user_by_email(email_or_token)
        if not user:
            return False
        g.current_user = user
        g.token_used = False
        return user.verify_password(password)
    else:
        user = m.User.load_user_by_token(email_or_token)
        if not user:
            return False
        g.current_user = user
        g.token_used = True
        return g.current_user is not None


@api.before_request
@auth.login_required
def before_request_hook():
    print(f'{__name__}: before_request hook, headers: {request}, user: {g.current_user}')
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('unconfirmed account')


@api.route('/token/generate', methods=['POST'])
def generate_token():
    print(f'{__name__}: generate_token, current_user: {g.current_user.is_anonymous()}, token used: {g.token_used}')
    if not g.current_user.is_anonymous() and not g.token_used:
        print(f'{__name__}:: current_user: {g.current_user}, token used: {g.token_used}')
        return jsonify({AUTH_TOKEN_KEY: g.current_user.generate_user_token(), AUTH_TOKEN_EXP_KEY: AUTH_TOKEN_EXP_VAL})
    else:
        abort(401)
        # return jsonify(False)


@api.route('/test', methods=['POST', 'GET'])
def test_rest_api():
    if request.method == 'GET':
        return g.current_user.to_json()
    elif request.method == 'POST':
        return {'request_method': 'POST', 'request_json': request.json,'user': g.current_user.to_json()}
    else:
        return jsonify({'error': 'It\'s fucked up'})

