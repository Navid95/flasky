import app.api as api_v1
import app.models as m
import app.api.authentication as authentication
from flask import g, request, jsonify

api = api_v1.api
auth = authentication.auth


# TODO add CRUD end points and functionality


@api.route('/user/find/all', methods=['GET'])
def user_find_all():
    """

    API to return the list of all users.

    :return: list of users
    """
    return [user.to_json() for user in m.User.__find_all__()]


# TODO add admin permission required
@api.route('/user/create', methods=['POST'])
def user_create():
    return m.User.persist(m.User.from_json(request.get_json())).to_json()


# TODO add admin permission required
@api.route('/user/findbyid/<id>', methods=['GET'])
def user_find_by_id(id):
    return m.load_user(id).to_json()


