# flask server
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 3333
FLASK_DEBUG = False
UPLOAD_FOLDER = './static/upload/'
ALLOWED_EXTENSIONS = set(['bmp', 'jpg', 'png', 'jpeg'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# train net
IS_USE_HALF = True
BATCH_SIZE = 256
EPOCHS = 10
PATH = 'model/fruit/wrn22.pth'
IS_LOAD_MODEL = True
DATASET_TRAIN_ROOT_PATH = 'data/FRUIT/Training/'
DATASET_TEST_ROOT_PATH = 'data/FRUIT/Test/'

# mysql
HOST = "localhost"
PORT = 3306
USER = "root"
PASSWD = "1qaz2wsx"
DB = "classify"
IS_PRINT_SQL = True
