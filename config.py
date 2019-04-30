# flask server
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 3333
FLASK_DEBUG = False
UPLOAD_FOLDER = './static/upload/'
ALLOWED_EXTENSIONS = set(['bmp', 'jpg', 'png', 'jpeg'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# net
BATCH_SIZE = 512
EPOCHS = 0
PATH = 'model/wrn22.pth'
IS_LOAD_MODEL = True