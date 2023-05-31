from flask import Blueprint
from . import routes, forms

main = Blueprint('main', __name__)

# Import the routes module to link it with the blueprint
import assessment_app.main.routes
