import socket
import threading
import time
from stats import Stats

import numpy as np
import libh264decoder

class Tello:
    def __init__(self, local_ip, local_port):
        #self.local_ip = ''
        #self.local_port = 8889
        self.decoder = libh264decoder.H264Decoder()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket.bind((local_ip, local_port))

        # thread for receiving cmd ack
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889
        self.tello_address = (self.tello_ip, self.tello_port)
        self.log = []

        self.MAX_TIME_OUT = 10.0

        # カメラ関連
        self.socket.sendto(b'command', self.tello_address)
        print('sent: command')
        # Enable video stream. ビデオ画像取得を可能にする
        self.socket.sendto(b'streamon', self.tello_address)
        print('sent: streamon')

        self.local_video_port = 11111# ビデオ受信用のポート
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_video.bind(("0.0.0.0", self.local_video_port))

        self.frame = None# numpy array BGR?
        self.is_freeze = False
        self.last_frame = None

        # ビデオ受信用のスレッド
        self.receive_video_thread = threading.Thread(target=self._receive_video_thread)
        self.receive_video_thread.daemon = True
        self.receive_video_thread.start()

    def send_command(self, command):
        """
        Send a command to the ip address. Will be blocked until
        the last command receives an 'OK'.
        If the command fails (either b/c time out or error),
        will try to resend the command
        :param command: (str) the command to send
        :param ip: (str) the ip of Tello
        :return: The latest command response
        """
        self.log.append(Stats(command, len(self.log)))

        self.socket.sendto(command.encode('utf-8'), self.tello_address)
        print('sending command: %s to %s' % (command, self.tello_ip))

        start = time.time()
        while not self.log[-1].got_response():
            now = time.time()
            diff = now - start
            if diff > self.MAX_TIME_OUT:
                print('Max timeout exceeded... command %s' % command)
                # TODO: is timeout considered failure or next command still get executed
                # now, next one got executed
                return
        print('Done!!! sent command: %s to %s' % (command, self.tello_ip))
    
    def read(self):
        return self.frame

    def _receive_thread(self):
        """Listen to responses from the Tello.

        Runs as a thread, sets self.response to whatever the Tello last returned.

        """
        while True:
            try:
                self.response, ip = self.socket.recvfrom(1024)
                print('from %s: %s' % (ip, self.response))

                self.log[-1].add_response(self.response)
            except socket.error:
                print("Caught exception socket.error : %s" % exc)

    def _receive_video_thread(self):
        packet_data = b''
        while True:
            try:
                # socket_video から受信
                # データがタプルで帰ってくる
                res_string, ip = self.socket_video.recvfrom(2048)

                packet_data += res_string

                if len(res_string) != 1460:
                    for frame in self._h264_decode(packet_data):
                        self.frame = frame
                    packet_data = b''
            
            except socket.error as exc:
                print(("Caught exception socket.error : %s" % exc))

    def _h264_decode(self, packet_data):
        res_frame_list = []
        frames = self.decoder.decode(packet_data)

        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                # bufferをndarrayに変換する
                # frameはバッファーとして読み込むもの
                # dtype 配列を返すときの要素のデータ型
                # count いくつのアイテムを読み込むか
                frame = np.frombuffer(frame, dtype = np.ubyte, count = len(frame))
                frame = (frame.reshape((h, ls//3, 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)
        
        return res_frame_list

    def on_close(self):
        pass
        # for ip in self.tello_ip_list:
        #     self.socket.sendto('land'.encode('utf-8'), (ip, 8889))
        # self.socket.close()

    def get_log(self):
        return self.log

