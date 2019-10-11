from App.Camera import camera
from flask import Flask, request, redirect, url_for
from werkzeug import SharedDataMiddleware
import numpy as np
import cv2
import time
from App.Camera.models.video import Video
from App.Camera.models.base import Deamon

base_img1 = cv2.imread("App\\Camera\\static\\base1.jpg", 0)
base_img2 = cv2.imread("App\\Camera\\static\\base1.jpg", 0)
base_img3 = cv2.imread("App\\Camera\\static\\base1.jpg", 0)
folder_path1 = 'D:\\camera_test\\tyre pump\\out1\\'
folder_path2 = 'D:\\camera_test\\tyre pump\\out2\\'
folder_path3 = 'D:\\camera_test\\tyre pump\\out3\\'
rtsp1 = 'rtsp://admin:ABSCMH@192.168.0.230:554/h264/ch1/main/av_stream'
rtsp2 = 'rtsp://admin:BUVNJG@192.168.0.233:554/h264/ch1/main/av_stream'
rtsp3 = 'rtsp://admin:LC525F06@192.168.0.231:554/cam/realmonitor?channel=1&subtype=0'
threshold1 = 28
threshold2 = 35
threshold3 = 30
isShowMatch1 = True
isShowMatch2 = True
isShowMatch3 = True
shape1 = (580,2000,470,1650)
shape2 = (200,700,480,920)
shape3 = (310,1100,510,1470)
isClassify1 = True
isClassify2 = True
isClassify3 = True

deamon = Deamon()
deamon.add_video('video1', folder_path1, base_img1, rtsp1, threshold1, isShowMatch1, shape1, isClassify1)
deamon.add_video('video2', folder_path2, base_img2, rtsp2, threshold2, isShowMatch2, shape2, isClassify2)
deamon.add_video('video3', folder_path3, base_img3, rtsp3, threshold3, isShowMatch3, shape3, isClassify3)


@camera.route('/')
def root():
    return 'hello camera'


@camera.route('/start', methods=['Post', 'Get'])
def start():
    deamon.start()
    return str(deamon.is_run())

@camera.route('/stop',methods=['Post','Get'])
def stop():
    deamon.stop()
    return str(deamon.is_run())


@camera.route('/status', methods=['Post','Get'])
def status():
    return deamon.json()
