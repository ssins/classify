import numpy as np
import cv2
from App.Camera.models.video import Video
import time
import os
from multiprocessing import Process
import psutil
import json


class Base(Process):
    def __init__(self):
        super().__init__()
        self.videos = []
        self.stoped = False
        self.delay = 3

    def run(self):
        self.run_videos()

    def add_videos(self, videos):
        self.videos = videos

    def get_videos(self):
        return self.videos

    def run_videos(self):
        for v in self.videos:
            if v.open:
                v.get_new_monitor()
                v.monitor.daemon = True
                v.monitor.start()
                time.sleep(5)
                print(v.name, v.monitor.is_alive())
        while True:
            if not self.is_father_alive():
                exit()
            time.sleep(self.delay)
            for v in self.videos:
                if not v.monitor.is_alive() and v.open:
                    v.get_new_monitor()
                    v.monitor.daemon = True
                    v.monitor.start()

    def is_father_alive(self):
        return os.getppid() in psutil.pids()


class Deamon():
    def __init__(self):
        self.videos = []
        self.base = Base()

    def is_run(self):
        return self.base.is_alive()

    def start(self, delay=3):
        if self.base.is_alive():
            self.stop()
        self.base = Base()
        self.base.delay = delay
        self.base.add_videos(self.videos)
        self.base.start()

    def stop(self):
        self.base.terminate()
        self.base.join()

    def add_video(self, name, out_path, base_img, rtsp, threshold, isShowMatch, shape=None, isClassify=False, open=True):
        v = Video(name, out_path, base_img, rtsp, threshold, isShowMatch, shape, isClassify, open)
        self.videos.append(v)
        return self.videos

    def remove_video(self, name):
        videos = []
        for v in self.videos:
            if v.name != name:
                videos.append(v)
        self.videos = videos
        return self.videos

    def close_video(self, name):
        for v in self.videos:
            if v.name == name:
                v.open = False
        return self.videos

    def open_video(self, name):
        for v in self.videos:
            if v.name == name:
                v.open = True
        return self.videos

    def json(self):
        out = {}
        out['state'] = 'running' if self.is_run() else 'stoped'
        out['videos'] = []
        for v in self.base.videos:
            s = {}
            s['name'] = v.name
            s['opened'] = v.open
            s['rtsp'] = v.rtsp
        return json.dumps(out)
