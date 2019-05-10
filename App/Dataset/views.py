from App.Dataset import dataset
from App.Dataset.controllers import *
from flask import Flask, request, redirect
from werkzeug import SharedDataMiddleware

@dataset.route('/upload_pic',methods=['GET', 'POST'])
def upload_pic():
    if request.method == 'POST':
        file = request.files['file']
        filename = upload_files(file)
        return filename
        #return redirect(url_for('classify', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
@dataset.route('/classify', methods=['POST', 'GET'])
def classify():
    filename = request.args.get('filename', '')
    if filename != '':
        return classify_pic([filename])
    return 'file not exist'