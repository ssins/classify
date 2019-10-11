from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from flask import redirect, url_for, request
from App import create_app
from App.models import *
import json

import shutil
import zxing
import os

app, db = create_app()


@app.route('/')
def root():
    return redirect(url_for('index.root'))

# # 初始化数据库
# @app.route('/init')
# def init():
#     try:
#         db.drop_all()
#         db.create_all()
#     except:
#         return 'fail'
#     return 'success'

@app.route('/test')
def test():
    reader = zxing.BarCodeReader()
    shutil.copy("C:\\Users\\admin\\PycharmProjects\\jiliangyuan_classify\\data\\test.jpg", "tmp\\tmp.jpg")
    barcode = reader.decode("tmp/tmp.jpg")
    os.remove("tmp\\tmp.jpg")
    return barcode.parsed

@app.route('/upload_qrcode')
def upload_qrcode():
    print('\033[32m')
    result = request.args.get('result', '')
    if not result:
        return json.dumps({'result':'failed'})
    print('>>>>>>>>>> 收到二维码解析结果为：%s' % (result))
    print('\033[0m')
    return json.dumps({'result':'success'})

if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
