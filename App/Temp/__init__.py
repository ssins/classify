import os
from flask import Blueprint
from config import BASE_DIR

temp = Blueprint('temp', __name__, 
                template_folder=os.path.join(BASE_DIR,'App/Temp/template'),
                static_folder=os.path.join(BASE_DIR,'App/Temp/static'))
static_folder = os.path.join(BASE_DIR,'App/Temp/static')

from App.Temp import views
