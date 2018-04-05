from socket import *
import threading
import pyaudio
import wave
import sys
import zlib
import struct
import pickle
import time
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 0.5


class GetAudio(threading.Thread):
    def __init__(self, port, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.address = ('', port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        self.pa = pyaudio.PyAudio()
        self.stream = None

    def __del__(self):
        self.sock.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.pa.terminate()

    def run(self):
        print("Audio receiver is starting...")
        self.sock.bind(self.address)
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        print("Audio receiver has started!")
        data = "".encode("utf-8")
        buffer_size = struct.calcsize("L")
        self.stream = self.pa.open(format=FORMAT,
                                   channels=CHANNELS,
                                   rate=RATE,
                                   output=True,
                                   frames_per_buffer=CHUNK
                                   )
        while True:
            while len(data) < buffer_size:
                data += conn.recv(81920)
            packed_size = data[:buffer_size]
            data = data[buffer_size:]
            msg_size = struct.unpack("L", packed_size)[0]
            while len(data) < msg_size:
                data += conn.recv(81920)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frames = pickle.loads(frame_data)
            for frame in frames:
                self.stream.write(frame, CHUNK)


class SendAudio(threading.Thread):
    def __init__(self, ip, port, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.address = (ip, port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        self.pa = pyaudio.PyAudio()
        self.stream = None

    def __del__(self):
        self.sock.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.pa.terminate()

    def run(self):
        print("Audio sender is starting...")
        while True:
            try:
                self.sock.connect(self.address)
                break
            except:
                time.sleep(3)
                continue
        print("Audio sender has started!")
        self.stream = self.pa.open(format=FORMAT,
                                   channels=CHANNELS,
                                   rate=RATE,
                                   input=True,
                                   frames_per_buffer=CHUNK)
        while self.stream.is_active():
            frames = []
            for i in range(int(RATE/CHUNK*RECORD_SECONDS)):
                data = self.stream.read(CHUNK)
                frames.append(data)
            sdata = pickle.dumps(frames)
            try:
                self.sock.sendall(struct.pack("L", len(sdata))+sdata)
            except:
                break
