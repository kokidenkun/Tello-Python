'''

Telloの起動方法
 1) スイッチを1回押し、オレンジの点滅状態にする
 2) PCからWiFi接続

ポートを使っているプロセスを調べるコマンド
 sudo fuser -n udp 8889 -n udp 11111
'''

import socket
import threading
import time
from stats import Stats

import numpy as np
import libh264decoder


class Tello:
    def __init__(self, local_ip= '0.0.0.0', local_port=8889, command_timeout=0.3, video=True):

        self.command_timeout = command_timeout
        self.abort_flag = False
        self.response = None
        self.log = []
        self.MAX_TIME_OUT = 10.0
        self.frame = None # numpy array BGR?
        self.is_freeze = False
        self.last_frame = None

        # Telloにコマンドを送りつけるためのソケットアドレスの作成
        self.tello_ip = '192.168.10.1'
        self.tello_port = 8889
        self.tello_address = (self.tello_ip, self.tello_port)

        # コマンド送信、期待情報取得用のソケットの生成
        self.local_ip = local_ip
        self.local_port = local_port
        self.decoder = libh264decoder.H264Decoder()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for sending cmd
        self.socket.bind((local_ip, local_port))


        # Telloとの通信を開始する
        self.socket.sendto(b'command', self.tello_address)
        self.response, ip = self.socket.recvfrom(1024)
        print('(3_3) First Contact:: ',self.response)  # OKと表示されるはず 

        # 上で"OK"をもらってから、受信スレッドを回す 
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        if video:
            # ビデオ受信用のUDPポートを開いておく
            self.local_video_port = 11111 # ビデオ受信用のポート
            self.socket_video = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_video.bind(("0.0.0.0", self.local_video_port))

            # ビデオ受信用のスレッド
            self.receive_video_thread = threading.Thread(target=self._receive_video_thread)
            self.receive_video_thread.daemon = True
            self.receive_video_thread.start()
        
            # TelloにH264ビデオの配信を指示する
            self.socket.sendto(b'streamon', self.tello_address)
            print('sent: streamon')


    def send_command(self, command):
        """
        Telloへコマンドを送信し，応答を待つ
        :param command: 送信するコマンド
        :return (str): Telloの応答
        """
        print (">> send cmd: {}".format(command))
        self.abort_flag = False		# 中断フラグを倒す
        timer = threading.Timer(self.command_timeout, self.set_abort_flag)		# タイムアウト時間が立ったらフラグを立てるタイマースレッドを作成
        
        self.socket.sendto(command.encode('utf-8'), self.tello_address)		# コマンドを送信
        
        timer.start()	# スレッドスタート
        while self.response is None:		# タイムアウト前に応答が来たらwhile終了
            if self.abort_flag is True:		# タイムアウト時刻になったらブレイク
                break
        timer.cancel()	# スレッド中断
        
        if self.response is None:		# 応答データが無い時
            response = 'none_response'
        else:							# 応答データがあるとき
            response = self.response.decode('utf-8')
        

        print('(@_@)---> ',response)
        self.response = None	# _receive_threadスレッドが次の応答を入れてくれるので，ここでは空にしておく
        
        return response		# 今回の応答データを返す

    def set_abort_flag(self):
        """
        self.abort_flagのフラグをTrueにする
        send_command関数の中のタイマーで呼ばれる．
        この関数が呼ばれるということは，応答が来なくてタイムアウトした，ということ．
        """
        
        self.abort_flag = True

    def get_battery(self):
        """
        バッテリー残量をパーセンテージで返す
        Returns:
        int: バッテリー残量のパーセンテージ
        """
        print("get_battery")
        battery = self.send_command('battery?')
        try:
            battery = int(battery)
        except:
            pass
        return battery
    
    def read(self):
        return self.frame

    def _receive_thread(self):
        while True:
            try:
                self.response, ip = self.socket.recvfrom(3000)		# Telloからの応答を受信（最大3000バイトまで一度に受け取れる）
				#print(self.response)
            except socket.error as exc:		# エラー時の処理
                print ("Caught exception socket.error : %s" % exc)


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

