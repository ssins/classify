import os
from flask import Blueprint
from config import BASE_DIR

ocr = Blueprint('ocr', __name__, 
                template_folder=os.path.join(BASE_DIR,'App/Ocr/template'),
                static_folder=os.path.join(BASE_DIR,'App/Ocr/static'))
static_folder = os.path.join(BASE_DIR,'App/Ocr/static')

from App.Ocr import views
