from App.Dataset import dataset
from App.Dataset.controllers import *
from flask import Flask, request, redirect
from werkzeug import SharedDataMiddleware


@dataset.route('/upload_pic', methods=['GET', 'POST'])
def upload_pic():
    if request.method == 'POST':
        file = request.files['file']
        filename = upload_files(file)
        return filename
        #return redirect(url_for('net.classify', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@dataset.route('/add', methods=['POST'])
def add_ds():
    name = request.form.get('name')
    root_path = request.form.get('root_path')
    if name and root_path:
        return add_data_set(name, root_path)
    return 'args error', 400


@dataset.route('/update', methods=['POST'])
def update_ds():
    name = request.form.get('name')
    root_path = request.form.get('root_path')
    if name and root_path:
        return update_data_set(name, root_path)
    return 'args error', 400


@dataset.route('/delete', methods=['POST'])
def delete_ds():
    name = request.form.get('name')
    if name:
        return delete_data_set(name)
    return 'args error', 400


@dataset.route('/init', methods=['POST'])
def init_ds():
    name = request.form.get('name')
    root_path = request.form.get('root_path')
    if name:
        return init_data_set(name, root_path)
    return 'args error', 400
