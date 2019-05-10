import os
from werkzeug import secure_filename
from App.Dataset import static_folder
from config import ALLOWED_EXTENSIONS
from flask import redirect, url_for


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_files(file, data_set_name=''):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pre_path = os.path.join(static_folder, 'upload', data_set_name)
        if not os.path.exists(pre_path):
            os.makedirs(pre_path)
        path = os.path.join(pre_path, filename)
        file.save(path)
        return redirect(url_for('net.classify', path=path))
