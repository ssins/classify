from App.Net import net
from App.Dataset import static_folder as ds_folder
from App.Net.controllers import *
from flask import request


@net.route('/classify', methods=['POST','GET'])
def classify():
    path = request.args.get('path', '')
    if not path:
        filename = request.args.get('file_name', '')
        netname = request.args.get('net_name', '')
        path = os.path.join(ds_folder, netname, filename)
    return classify_pic([path])