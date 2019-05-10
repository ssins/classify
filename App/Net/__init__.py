from flask import Blueprint
import os
from config import BASE_DIR

net = Blueprint('net', __name__, 
                  template_folder=os.path.join(BASE_DIR,'App/Net/template'),
                 static_folder=os.path.join(BASE_DIR,'App/Net/static'))

static_folder = os.path.join(BASE_DIR,'App/Net/static')

from App.Net import views