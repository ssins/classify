import os
from flask import Blueprint
from config import BASE_DIR

camera = Blueprint('camera', __name__, 
                template_folder=os.path.join(BASE_DIR,'App/Camera/template'),
                static_folder=os.path.join(BASE_DIR,'App/Camera/static'))
static_folder = os.path.join(BASE_DIR,'App/Camera/static')

from App.Camera import views
