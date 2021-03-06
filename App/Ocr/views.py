from App.Ocr import ocr
from App.Ocr.controllers import *
from flask import Flask, request, redirect

@ocr.route('/', methods=['GET'])
def root():
    return redirect(url_for('ocr.upload_pic'))

@ocr.route('/upload_pic', methods=['GET', 'POST'])
def upload_pic():
    if request.method == 'POST':
        file = request.files['file']
        filename = upload_files(file)
        if filename is not None:
            return ocr_baidu(filename)
        return filename
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
