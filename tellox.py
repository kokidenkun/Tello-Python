
import socket
import fcntl
import queue
import os
import select
import threading
import time
import random
import numpy as np
import libh264decoder
import datetime

class Tello:
    def __init__(self, video=True):

        self.frame = None

        self.stat = None

        self.cmd_que = queue.Queue()
        self.cmd_now = None

        self.tello_address = ('192.168.10.1', 8889)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('0.0.0.0', 8889))
        self.socket.connect(self.tello_address)
        flag = fcntl.fcntl(self.socket, fcntl.F_GETFL)
        fcntl.fcntl(self.socket, fcntl.F_GETFL, flag | os.O_NONBLOCK)

        self.put_command('command')

        if video:
            self.receive_video_thread = threading.Thread(target=self._receive_video_thread)
            self.receive_video_thread.daemon = True
            self.receive_video_thread.start()


        self.command_thread = threading.Thread(target=self._command_thread)
        self.command_thread.daemon = True
        self.command_thread.start()

        self.receive_stat_thread = threading.Thread(target=self._receive_stat_thread)
        self.receive_stat_thread.daemon = True
        self.receive_stat_thread.start()


    def put_command(self, cmd):
        self.cmd_que.put(cmd)

    def get_stat(self):
        return self.stat

    def get_frame(self):
        return self.frame

    
    #-------------------------------------

    def _command_thread(self):
        #simple_command=['battery?', 'height?', 'speed?', 'time?']
        while True:
            time.sleep(0.2) ## このsleepが短すぎると、送信コマンドと、その結果がずれてくるので注意
            if not self.cmd_que.empty():
                self.cmd_now = self.cmd_que.get()
                ret = self.__control(self.cmd_now)
                print(ret)
            # else:
            #     self.cmd_que.put(random.choice(simple_command))

    def __control(self, command):
        response = None
        self.socket.send(command.encode('utf-8'))
        rfds, _ , _ = select.select( [self.socket], [], [], 0.3 )
        if self.socket in rfds:
            response = self.socket.recv(3000)
            response = response.decode('utf-8')
        
        print(command, response)
        return response

    def _receive_stat_thread(self):
        self.socket_stat = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.socket_stat.bind(('0.0.0.0', 8890))
        self.socket_stat.connect(self.tello_address)
        
        while True:
            res_string = self.socket_stat.recv(2048)
            res_string = res_string.decode('utf-8')
            self.stat = dict([(x[0],x[1]) for x in [x.split(':') for x in res_string.strip().split(';')[0:-1]]])
            # print(datetime.datetime.now(), ", ", self.stat)

    
    def _receive_video_thread(self):
        self.decoder = libh264decoder.H264Decoder()
            
        self.local_video_port = 11111
        self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket_video.bind(("0.0.0.0", self.local_video_port))

        self.put_command('streamon')
        packet_data = b''
        while True:
            try:
                res_string, ip = self.socket_video.recvfrom(2048)
                packet_data += res_string
                if len(res_string) != 1460:
                    for frame in self._h264_decode(packet_data):
                        self.frame = frame
                    packet_data = b''
            except socket.error as exec:
                print(("Caught exception socket.error: %s" % exc))

    def _h264_decode(self, packet_data):
        res_frame_list = []
        frames = self.decoder.decode(packet_data)

        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                frame = np.frombuffer(frame, dtype = np.ubyte, count = len(frame))
                frame = (frame.reshape((h, ls//3, 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)

        return res_frame_list

