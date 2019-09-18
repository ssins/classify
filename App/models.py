from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class base():
    id = db.Column(db.Integer, primary_key=True)
    update_time = db.Column(db.TIMESTAMP)


class Data_set(db.Model, base):
    name = db.Column(db.String(255))
    root_path = db.Column(db.String(255))

    def __init__(self, name, root_path):
        self.name = name
        self.root_path = root_path

    def __repr__(self):
        return '<Data_set %r>' % self.name


class Image(db.Model, base):
    path = db.Column(db.String(255))
    label_id = db.Column(db.Integer, db.ForeignKey('label.id'))
    label = db.relationship(
        'Label', backref=db.backref('labels', lazy='dynamic'))
    data_set_id = db.Column(db.Integer, db.ForeignKey('data_set.id'))
    data_set = db.relationship(
        'Data_set', backref=db.backref('images', lazy='dynamic'))

    def __init__(self, path, label, data_set=None):
        self.path = path
        self.label = label
        self.data_set = label.data_set if label else data_set

    def __repr__(self):
        return '<Image %r>' % self.path


class Model(db.Model, base):
    path = db.Column(db.String(255))
    name = db.Column(db.String(255))
    data_set_id = db.Column(db.Integer, db.ForeignKey('data_set.id'))
    data_set = db.relationship(
        'Data_set', backref=db.backref('models', lazy='dynamic'))
    gpu_count = db.Column(db.Integer)
    is_half = db.Column(db.Boolean)

    def __init__(self, path, name, data_set, gpu_count=1, is_half=False):
        self.path = path
        self.name = name
        self.data_set = data_set
        self.gpu_count = gpu_count
        self.is_half = is_half

    def __repr__(self):
        return '<Model %r>' % self.path


class Label(db.Model, base):
    value = db.Column(db.String(255))
    idx = db.Column(db.Integer)
    data_set_id = db.Column(db.Integer, db.ForeignKey('data_set.id'))
    data_set = db.relationship(
        'Data_set', backref=db.backref('labels', lazy='dynamic'))

    def __init__(self, value, idx, data_set):
        self.value = value
        self.idx = idx
        self.data_set = data_set

    def __repr__(self):
        return '<Label %r>' % self.value
