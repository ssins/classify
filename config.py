import os
BASE_DIR = os.getcwd()

# flask server
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 3333
FLASK_DEBUG = False
UPLOAD_FOLDER = './static/upload/'
ALLOWED_EXTENSIONS = set(['bmp', 'jpg', 'png', 'jpeg'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123qaz...@www.ssins.cn:3306/classify'  # 数据库URI
SQLALCHEMY_TRACK_MODIFICATIONS = False  # 查询跟踪，不太需要，False，不占用额外的内存

# train net
IS_USE_HALF = True
DEFAULT_BATCH_SIZE = 16
DEFAULT_EPOCHS = 100
PATH = 'model/something/wrn22_256_16_p.pth'
# IS_LOAD_MODEL = True
# DATASET_TRAIN_ROOT_PATH = 'data/FRUIT/Training/'
# DATASET_TEST_ROOT_PATH = 'data/FRUIT/Test/'

# mysql
HOST = "www.ssins.cn"
PORT = 3306
USER = "root"
PASSWD = "123qaz..."
DB = "classify"
IS_PRINT_SQL = False

# dataset
IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.ppm',
                  '.bmp', '.pgm', '.tif', '.tiff', 'webp']
