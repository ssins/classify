import os
from werkzeug import secure_filename
from App.Dataset import static_folder
from App.models import db, Data_set, Label, Image, Model
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


def add_data_set(name, root_path):
    if Data_set.query.filter_by(name=name).first():
        return 'name exist', 403
    ds = Data_set(name, root_path)
    db.session.add(ds)
    db.session.commit()
    return 'success'


def update_data_set(name, root_path):
    ds = Data_set.query.filter_by(name=name).first()
    if not ds:
        return 'name not exist', 403
    ds.root_path = root_path
    db.session.add(ds)
    db.session.commit()
    return 'success'


def delete_data_set(name):
    ds = Data_set.query.filter_by(name=name).first()
    if not ds:
        return 'name not exist', 403
    # label = Label(None, None, ds)
    # img = Image(None, None, ds)
    # model = Model(None, None, ds, None, None)
    db.session.delete(ds)
    # db.session.delete(label)
    # db.session.delete(img)
    # db.session.delete(model)
    db.session.commit()
    return 'success'