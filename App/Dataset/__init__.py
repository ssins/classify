import os
from flask import Blueprint
from config import BASE_DIR

dataset = Blueprint('dataset', __name__, 
                template_folder=os.path.join(BASE_DIR,'App/Dataset/template'),
                static_folder=os.path.join(BASE_DIR,'App/Dataset/static'))
static_folder = os.path.join(BASE_DIR,'App/Dataset/static')

from App.Dataset import views