from flask import Flask
import os
from flask import Flask, render_template, Response, url_for
from audioswap import *
from vedioswap import *
import socket
import pyaudio

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/constart")
def constart():
    IP = '127.0.0.1'
    PORT = 10087
    LEVEL = 1
    VERSION = 4
    vsend = SendVideo(IP, PORT, LEVEL, VERSION)
    vget = GetVideo(PORT, VERSION)
    asend = SendAudio(IP, PORT+1, VERSION)
    aget = GetAudio(PORT+1, VERSION)
    vsend.start()
    asend.start()
    time.sleep(1)
    aget.start()
    return Response(vget.run(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/frame")
def frame():
    constart()

if __name__ == '__main__':
    app.run()
