import os
import sys
from werkzeug import secure_filename
from App.Ocr import static_folder
from config import ALLOWED_EXTENSIONS, IMG_EXTENSIONS
from flask import redirect, url_for
from aip import AipOcr
import webbrowser
import urllib
import json

""" 你的 APPID AK SK """
APP_ID = '17278342'
API_KEY = 'iSyjMnVqrLpeGockb8yjG0Xq'
SECRET_KEY = 'bvUGc2svDMbVS9zlC308Y4xZSI9PPlwO'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

def _allowed_file(filename):
    filename_lower = filename.lower()
    return any(filename_lower.endswith(ext) for ext in ALLOWED_EXTENSIONS)

def upload_files(file):
    if file and _allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pre_path = os.path.join(static_folder, 'upload')
        if not os.path.exists(pre_path):
            os.makedirs(pre_path)
        path = os.path.join(pre_path, filename)
        file.save(path)
        return path
    return None

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def ocr_baidu(filename):
    print('\033[32m')
    image = get_file_content(filename)

    """ 调用通用文字识别, 图片参数为本地图片 """
    result = client.basicGeneral(image)
    if result.get('words_result_num') is not None:
        print(">>>>>>>>>> 识别到文字段的数量为：%s" % result['words_result_num'])
        if result['words_result_num'] > 0 and result.get('words_result') is not None:
            words = result['words_result']
            words_str = ''
            print(">>>>>>>>>> 识别结果：")
            for idx, word in enumerate(words):
                print("             [%s] %s" % (idx+1, word['words']))
                if idx == 0:
                    words_str += word['words']
                if word['words'].find('型号') >= 0:
                    words_str += ' + ' + word['words']
            webbrowser.open("https://www.baidu.com/s?wd=%s" %
                            (urllib.parse.quote(words_str)))
        print('\033[0m')
        return json.dumps(result)
    else:
        print('\033[3;31m')
        print(">>>>>>>>>> 识别失败")
        print('\033[0m')
        return "识别失败", 400

