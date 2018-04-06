from socket import *
import threading
import cv2
import struct
import pickle
import time
import zlib


class GetVideo(threading.Thread):
    def __init__(self, port, version):
        threading.Thread.__init__(self)
        # self.setDaemon(True)
        self.address = ('', port)
        self.conn = socket()
        self.addr = ''
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)

    def __del__(self):
        self.sock.close()

    def run(self):
        print("Video receiver is waiting for connection")
        self.sock.bind(self.address)
        self.sock.listen(1)
        self.conn, self.addr = self.sock.accept()
        print("Video receiver has connect!")
        frame = "".encode("utf-8")
        buff_size = struct.calcsize("L")
        while True:
            while len(frame) < buff_size:
                frame += self.conn.recv(81920)
            packed_size = frame[:buff_size]
            frame = frame[buff_size:]
            msg_size = struct.unpack("L", packed_size)[0]
            frame += self.conn.recv(msg_size)
            while len(frame) < msg_size:
                frame += self.conn.recv(81920)
            fframe_data = frame[:msg_size]
            frame = frame[msg_size:]
            frame_data = zlib.decompress(fframe_data)
            framee = pickle.loads(frame_data)
            yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + framee + b'\r\n')


class SendVideo(threading.Thread):
    def __init__(self, ip, port, level, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.address = (ip, port)
        if level <= 3:
            self.interval = level
        else:
            self.interval = 3
        self.fx = 1 / (self.interval + 1)
        if self.fx < 0.3:
            self.fx = 0.3
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        self.cap = cv2.VideoCapture(0)

    def __del__(self):
        self.sock.close()
        self.cap.release()

    def connect(self):
        print("Video sender is starting...")
        try:
            self.sock.settimeout(8)
            self.sock.connect(self.address)
            self.sock.settimeout(None)
        except timeout:
            return 'timeout'
        print("Video sender has started!")
        return 'ok'

    def run(self):
        self.sock.connect(self.address)
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            rframe = cv2.resize(frame, (0, 0), fx=self.fx, fy=self.fx)
            bframe = cv2.imencode('.jpg', rframe)[1].tobytes()
            data = pickle.dumps(bframe)
            dataa = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
            try:
                self.sock.sendall(struct.pack("L", len(dataa)) + dataa)
            except:
                break
            for i in range(self.interval):
                self.cap.read()
