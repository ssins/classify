from App.Net import net
from App.Dataset import static_folder as ds_folder
from App.Net.controllers import *
from flask import request


@net.route('/classify', methods=['GET'])
def classify():
    path = request.args.get('path', '')
    if not path:
        filename = request.args.get('file_name', '')
        netname = request.args.get('net_name', '')
        path = os.path.join(ds_folder, netname, filename)
    return classify_pic([path])

@net.route('/train', methods=['GET'])
def train():
    name = request.args.get('name', '')
    if not name:
        return train_net(name)
    return train_net()
    
