import os
import sys
from werkzeug import secure_filename
from App.Dataset import static_folder
from App.models import db, Data_set, Label, Image, Model
from config import ALLOWED_EXTENSIONS, IMG_EXTENSIONS
from flask import redirect, url_for


def _allowed_file(filename):
    filename_lower = filename.lower()
    return any(filename_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS)


def _is_img_file(filename):
    filename_lower = filename.lower()
    return any(filename_lower.endswith(ext) for ext in IMG_EXTENSIONS)


def _find_classes(dir):
    if sys.version_info >= (3, 5):
        classes = [d.name for d in os.scandir(dir) if d.is_dir()]
    else:
        classes = [d for d in os.listdir(
            dir) if os.path.isdir(os.path.join(dir, d))]
    classes.sort()
    class_to_idx = {classes[i]: i for i in range(len(classes))}
    return classes, class_to_idx


def _find_files(dir):
    if sys.version_info >= (3, 5):
        files = [d.name for d in os.scandir(dir) if d.is_file()]
    else:
        files = [d for d in os.listdir(
            dir) if os.path.isfile(os.path.join(dir, d))]
    return files


def upload_files(file, data_set_name=''):
    if file and _allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pre_path = os.path.join(static_folder, 'upload', data_set_name)
        if not os.path.exists(pre_path):
            os.makedirs(pre_path)
        path = os.path.join(pre_path, filename)
        file.save(path)
        return redirect(url_for('net.classify', path=path))
    return 'file not exist', 403


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
    images = Image.query.filter_by(data_set_id=ds.id).all()
    models = Model.query.filter_by(data_set_id=ds.id).all()
    labels = Label.query.filter_by(data_set_id=ds.id).all()
    for image in images:
        db.session.delete(image)
    for model in models:
        db.session.delete(model)
    for label in labels:
        db.session.delete(label)
    db.session.delete(ds)
    db.session.commit()
    return 'success'


def init_data_set(name, root_path):
    ds = Data_set.query.filter_by(name=name).first()
    if not ds:
        return 'name not exist', 403
    if not root_path:
        root_path = ds.root_path
    else:
        ds.root_path = root_path
        db.session.add(ds)
    images = Image.query.filter_by(data_set_id=ds.id).all()
    models = Model.query.filter_by(data_set_id=ds.id).all()
    labels = Label.query.filter_by(data_set_id=ds.id).all()
    for image in images:
        db.session.delete(image)
    for model in models:
        db.session.delete(model)
    for label in labels:
        db.session.delete(label)
    db.session.commit()
    classes, _ = _find_classes(root_path)
    count = 0
    labels = []
    for idx, lb in enumerate(classes):
        label = Label(lb, idx, ds)
        labels.append(label)
        db.session.add(label)
    db.session.commit()
    for label in labels:
        pre_path = os.path.join(root_path, label.value)
        files = _find_files(pre_path)
        for f in files:
            path = '/%s/%s' % (label.value, f)
            if _is_img_file(path):
                image = Image(path, label)
                db.session.add(image)
                count += 1
                if count % 100 == 0:
                    db.session.commit()
                    if count % 1000 == 0:
                        print('>>insert {} imgs'.format(count))
    return 'success'
