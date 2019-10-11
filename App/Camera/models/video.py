import numpy as np
import cv2
import time
import os
from multiprocessing import Process
import psutil
from App.Net.controllers import *
import json
import shutil
import zxing
import os


class Monitor(Process):

    translateMap = {
        'multimeter': '万用表',
        'pressure gauge': '压力表',
        'scissors': '剪刀',
        'screwdriver': '螺丝起子',
        'tyre pump': '打气筒'
    }

    def __init__(self, name, folder_path, base_img, rtsp, threshold, isShowMatch, shape=None, isClassify=False):
        super().__init__()
        self.name = name
        self.folder_path = folder_path
        self.base_img = base_img
        self.rtsp = rtsp
        self.alive = False
        self.threshold = threshold  # 匹配阈值
        self.isShowMatch = isShowMatch  # 是否显示匹配图
        self.shape = shape
        self.isClassify = isClassify  # 是否进行实时识别
        self.isShowClassify = False
        self.classifyResult = None
        self.isShowQrcode = False
        self.qrcodeResult = None

    def run(self):
        cap = cv2.VideoCapture(self.rtsp)
        i = 0
        img1 = self.base_img
        detector = cv2.ORB_create()
        kp1 = detector.detect(img1, None)
        kp1, des1 = detector.compute(img1, kp1)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)
        while True:
            if not self.is_father_alive():
                exit()
            ret, frame = cap.read()
            if frame is None:
                continue
            if self.shape is not None:
                frameShape = frame[self.shape[0]:self.shape[1], self.shape[2]:self.shape[3]]
            else:
                frameShape = frame
            img2 = cv2.cvtColor(frameShape, cv2.COLOR_BGR2GRAY)
            kp2 = detector.detect(img2, None)
            kp2, des2 = detector.compute(img2, kp2)
            matches = bf.knnMatch(des1, trainDescriptors=des2, k=2)
            good = [m for (m, n) in matches if m.distance < 0.75*n.distance]
            if len(good) < self.threshold:
                i += 1
                if i % 30 == 0:
                    t = time.time()
                    path = self.folder_path + time.strftime('%Y-%m-%d')
                    if not os.path.exists(path):
                        os.makedirs(path)
                    savePath = path + '\\' + self.name + '-' + \
                        str(int(round(t * 1000))) + '.jpg'
                    cv2.imwrite(savePath, frameShape)
                    i = 0
                    if self.isClassify:
                        self.classifyResult = classify_pic([savePath])
                        self.isShowClassify = True
                        # if os.path.exists("tmp\\"+self.name+".jpg"):
                        #     os.remove("tmp\\"+self.name+".jpg")
                        # reader = zxing.BarCodeReader()
                        # shutil.copy(savePath, "tmp\\"+self.name+".jpg")
                        # barcode = reader.decode("tmp/"+self.name+".jpg")
                        # if barcode is not None:
                        #     self.isShowQrcode = True
                        #     self.qrcodeResult = barcode.parsed
                        # else:
                        #     self.isShowQrcode = False
                    else:
                        self.isShowClassify = False
                        # self.isShowQrcode = False
            else:
                i = 0
                self.isShowClassify = False
                self.isShowQrcode = False

            if self.isShowMatch:
                # img3 = self.draw_matches(img1, kp1, img2, kp2, good[:50])
                img3 = self.draw_matches2(img2, kp2, good[:100])
                cv2.imshow(self.name, img3)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

    def is_father_alive(self):
        return os.getppid() in psutil.pids()

    def pid(self):
        return os.getpid()

    # 特征点匹配结果，显示检测图案和原图
    def draw_matches(self, img1, kp1, img2, kp2, matches):
        rows1 = img1.shape[0]
        cols1 = img1.shape[1]
        rows2 = img2.shape[0]
        cols2 = img2.shape[1]
        out = np.zeros((max([rows1, rows2]), cols1 + cols2, 3), dtype='uint8')
        out[:rows1, :cols1] = np.dstack([img1, img1, img1])
        out[:rows2, cols1:] = np.dstack([img2, img2, img2])
        for mat in matches:
            img1_idx = mat.queryIdx
            img2_idx = mat.trainIdx
            (x1, y1) = kp1[img1_idx].pt
            (x2, y2) = kp2[img2_idx].pt
            cv2.circle(out, (int(x1), int(y1)), 4, (255, 255, 0), 1)
            cv2.circle(out, (int(x2)+cols1, int(y2)), 4, (0, 255, 255), 1)
            cv2.line(out, (int(x1), int(y1)),
                     (int(x2)+cols1, int(y2)), (255, 0, 0), 1)
        return out

    # 仅显示摄像头图像
    def draw_matches2(self, img2, kp2, matches):
        rows2 = img2.shape[0]
        cols2 = img2.shape[1]
        out = np.zeros((rows2, cols2, 3), dtype='uint8')
        out[:rows2, :cols2] = np.dstack([img2, img2, img2])
        for mat in matches:
            img2_idx = mat.trainIdx
            (x2, y2) = kp2[img2_idx].pt
            cv2.circle(out, (int(x2), int(y2)), 4, (255, 255, 0), 1)
        cv2.putText(out, 'Points: ' + str(len(matches)),
                    (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
        if self.isShowClassify:
            result = json.loads(self.classifyResult)
            cv2.putText(out, 'Result: ' + result['result'][0],
                        (0, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            cv2.putText(out, 'Time: ' + str(result['time']),
                        (0, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            # print('\033[32m')
            # print('>>>>>>>>>> 图像识别结果为：%s' % (translateMap[result['result'][0]]))
            # print('\033[0m')
        if self.isShowQrcode:
            cv2.putText(out, 'QrCode: ' + self.qrcodeResult,
                        (0, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 2)
        
        return out


class Video():
    def __init__(self, name, folder_path, base_img, rtsp, threshold=25, isShowMatch=False, shape=None, isClassify=False, open=True):
        self.name = name
        self.folder_path = folder_path
        self.base_img = base_img
        self.rtsp = rtsp
        self.open = open
        self.threshold = threshold  # 匹配阈值
        self.isShowMatch = isShowMatch  # 是否显示匹配图
        self.shape = shape
        self.isClassify = isClassify
        self.monitor = Monitor(
            self.name, self.folder_path, self.base_img, self.rtsp, self.threshold, self.isShowMatch, self.shape, self.isClassify)

    def get_new_monitor(self):
        self.monitor = Monitor(
            self.name, self.folder_path, self.base_img, self.rtsp, self.threshold, self.isShowMatch, self.shape, self.isClassify)
        return self.monitor
