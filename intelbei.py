from flask import Flask
import os
from flask import Flask, render_template, Response, url_for, request, redirect
from audioswap import *
from vedioswap import *
import multiprocessing
import socket
import pyaudio
import threading

app = Flask(__name__)

IP = '192.168.1.106'
PORT = 10087
LEVEL = 2
VERSION = 4


aget = GetAudio(PORT + 1, VERSION)
vget = GetVideo(PORT, VERSION)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/kill', methods=['POST', 'GET'])
def kill():
    print(1)
    aget.conn.close()
    vget.conn.close()
    global aget
    aget = GetAudio(PORT + 1, VERSION)
    global  vget
    vget=GetVideo(PORT, VERSION)
    return redirect(url_for('main'))


@app.route('/error')
def error():
    return render_template('error.html')


@app.route("/go", methods=['POST'])
def go():
    if request.method == 'POST':
        global IP
        IP = request.form.get('IP', '')
        if IP:
            return render_template('index.html', stauts='ok')
        else:
            return redirect(url_for('error'))
    else:
        return redirect(url_for('error'))


@app.route("/constart")
def constart():
    try:
        vsend = SendVideo(IP, PORT, LEVEL, VERSION)
        asend = SendAudio(IP, PORT+1, VERSION)
        global vget
        global aget
        aget.start()
        vsend.start()
        asend.start()
        return Response(vget.run(), mimetype='multipart/x-mixed-replace; boundary=frame')
    except:
        return render_template("main.html")


if __name__ == '__main__':
    app.run()
