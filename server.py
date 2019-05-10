from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from flask import redirect, url_for
from App import create_app

app = create_app()


@app.route('/')
def root():
    return redirect(url_for('index.root'))


if __name__ == '__main__':
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
