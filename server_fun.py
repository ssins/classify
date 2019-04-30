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
    print('path:%s' % path)
    net_fun.main()
    return 'done'
