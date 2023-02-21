from flask import Blueprint

"""
Creating the Blueprints
"""

main = Blueprint('main', __name__)

from . import views, errors
import app.models as models


@main.app_context_processor
def inject_permissions():
    return dict(Permission=models.Permission)
