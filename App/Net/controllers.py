from App.Net import static_folder
import os
import net_fun
import json
from config import ALLOWED_EXTENSIONS
from torchvision import transforms

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def classify_pic(image_paths, net_name='something', model_name=None, model_id=None):
    images = []
    for path in image_paths:
        if os.path.exists(path) and allowed_file(path):
            images.append(path)
    if len(images) < 1:
        return "all files not exist"
    net = net_fun.NetFun(net_name)
    # net.load_data_set()
    net.load_model(model_name=model_name, model_id=model_id)
    pred, classify_time = net.classify(images=images)
    idx_to_class = net.idx_to_class
    data = {'time': classify_time, 'count': len(
        images), 'result': [idx_to_class[pred[j, 0].item()] for j in range(len(images))]}
    return json.dumps(data)

def train_net(net_name='camera'):
    # print(net_name)
    net = net_fun.NetFun(net_name)
    net.load_data_set()
    net.train()
    return "True"

