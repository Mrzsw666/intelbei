import os
from flask import Flask, render_template, Response, url_for
import socket

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('test.html')


def getFrame():
    host = '192.168.1.106'
    port = 8000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (host, port)
    s.bind(address)
    s.listen(1)
    conn, addr = s.accept()
    print('Connected by', addr)
    while True:
        lenn = conn.recv(4)
        lenth = int.from_bytes(lenn, 'big')
        frame = conn.recv(lenth)
        print(2)
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/get_video')
def get_video():
    return Response(getFrame(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run()


