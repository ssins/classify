import os
import net_fun

from flask import url_for
from werkzeug import secure_filename

from config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_files(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return 'success upload: %s' % url_for('uploaded_file', filename=filename)


def classify_pic(filename):
    filename = secure_filename(filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    # if os.path.exists(secure_filename(path)) and allowed_file(filename):
    #     image = cv2.imread(path)
    #     if image:
    return "todo"


def classify_pic_test():
    net = net_fun.NetFun()
    pred, labels, classify_time = net.classify()
    classes = net.classes
    for j in range(5 if 5 < net.batch_size else net.batch_size):
        print(classes[pred[j, 0]], '(', classes[labels[j]], ')')
    return 'classify {} images in {:.6f}s'.format(net.batch_size, classify_time)
