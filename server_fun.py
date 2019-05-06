import os
from flask import url_for
from werkzeug import secure_filename
import json

import net_fun
from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_files(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return filename


def classify_pic(filenames):
    images = []
    for filename in filenames:
        filename = secure_filename(filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(path) and allowed_file(filename):
            images.append(path)
    if len(images) < 1:
        return "all files not exist"
    net = net_fun.NetFun()
    pred, classify_time = net.classify(images=images)
    classes = net.classes
    data = [{'time': classify_time, 'count': len(
        images), 'result': [classes[pred[j, 0]] for j in range(len(images))]}]
    return json.dumps(data)


def classify_pic_test():
    net = net_fun.NetFun()
    pred, labels, classify_time = net.classify()
    classes = net.classes
    for j in range(5 if 5 < net.batch_size else net.batch_size):
        print(classes[pred[j, 0]], '(', classes[labels[j]], ')')
    return 'classify {} images in {:.6f}s'.format(net.batch_size, classify_time)
