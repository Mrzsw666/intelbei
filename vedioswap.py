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
        self.setDaemon(True)
        self.address = ('', port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)

    def __del__(self):
        self.sock.close()

    def run(self):
        print("Video receiver starting...")
        self.sock.bind(self.address)
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        print("Video receiver has sterted!")
        frame = "".encode("utf-8")
        buff_size = struct.calcsize("L")
        # cv2.namedWindow('Remote', cv2.WINDOW_NORMAL)
        while True:
            while len(frame) < buff_size:
                frame += conn.recv(81920)
            packed_size = frame[:buff_size]
            frame = frame[buff_size:]
            msg_size = struct.unpack("L", packed_size)[0]
            frame += conn.recv(msg_size)
            while len(frame) < msg_size:
                frame += conn.recv(81920)
            fframe_data = frame[:msg_size]
            frame = frame[msg_size:]
            #frame_data = zlib.decompress(fframe_data)
            #framee = pickle.loads(frame_data)
            print(len(fframe_data))
            '''
            cv2.imshow('Remote', framee)
            if cv2.waitKey(1) & 0xFF == 27:
                break
            '''
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + fframe_data + b'\r\n')


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

    def run(self):
        print("Video sender is starting...")
        while True:
            try:
                self.sock.connect(self.address)
                break
            except:
                time.sleep(5)
                continue
        print("Video sender has started!")
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            rframe = cv2.resize(frame, (0, 0), fx=self.fx, fy=self.fx)
            bframe = cv2.imencode('.jpg', rframe)[1].tobytes()
            #data = pickle.dumps(bframe)
            #dataa = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
            print(len(bframe))
            try:
                self.sock.sendall(struct.pack("L", len(bframe))+bframe)
            except:
                break
            for i in range(self.interval):
                self.cap.read()

