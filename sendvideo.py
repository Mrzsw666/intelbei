#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask
import socket
import time
# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)


def gen(camera):
    while True:
        frame = camera.get_frame()
        lenth = len(frame)
        lenth = lenth.to_bytes(4, 'big')
        client.sendall(lenth)
        print(1)
        client.sendall(frame)
        time.sleep(0.1)


# @app.route('/video_feed')
def video_feed():
    gen(Camera())

host = '192.168.1.106'
port = 8000
address = (host, port)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(address)
video_feed()
