from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from flask import redirect, url_for
from App import create_app
from App.models import *

app, db = create_app()


@app.route('/')
def root():
    return redirect(url_for('index.root'))

# 初始化数据库
@app.route('/init')
def init():
    try:
        db.drop_all()
        db.create_all()
    except:
        return 'fail'
    return 'success'

@app.route('/test')
def test():
    ds = Data_set.query.filter_by(name='fruit').first()
    for image in ds.images:
        print(image)
    return 'success'

if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
