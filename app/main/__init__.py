from flask import Blueprint

"""
Creating the Blueprints
"""

main = Blueprint('main', __name__)

from . import views, errors
