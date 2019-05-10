from App import create_app
from App.Index import index
from App.Dataset import dataset
from App.Net import net

from flask import redirect, url_for
from config import *

app = create_app()
app.register_blueprint(index, url_prefix='/index')
app.register_blueprint(dataset, url_prefix='/dataset')
app.register_blueprint(net, url_prefix='/net')


@app.route('/')
def root():
    return redirect(url_for('index.root'))


if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
