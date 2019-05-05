from flask import Flask, request, redirect
from werkzeug import SharedDataMiddleware

from config import *
from server_fun import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.add_url_rule('/uploads/<filename>', 'uploaded_file', build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads': app.config['UPLOAD_FOLDER']
})


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        filename = upload_files(file)
        return redirect(url_for('classify', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/classify', methods=['POST', 'GET'])
def classify():
    filename = request.args.get('filename', '')
    if filename != '':
        return classify_pic([filename, filename, filename])
    return 'file not exist'


# @app.route('/test', methods=['POST', 'GET'])
# def test():
#     return classify_pic_test()


if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
