from tellox import Tello
import sys
import time
import threading
from pygame.locals import *
import pygame
import cv2
import os

# スクリーンを使わないための設定(rootで行う必要がある)
os.putenv('SDL_VIDEODRIVER', 'dummy')

bat=-1

VIDEO = False

run = True

A_BUTTON = 0
B_BUTTON = 1
X_BUTTON = 2
Y_BUTTON = 3
LB_BUTTON = 4
RB_BUTTON = 5
BACK = 6
START = 7
LOGICOOL = 8

L_STICK_X = 0
L_STICK_Y = 1

R_STICK_X = 3
R_STICK_Y = 4

cmd_sc = ''

right_stick_x = 0
right_stick_y = 0

left_stick_x = 0
left_stick_y = 0

tello = Tello(video=True) # ビデオ配信有効
# tello = Tello(video=False)  # ビデオ配信無効

def main():
    # while True:
    #     print(tello.get_stat())
    #     time.sleep(1)
    # while not VIDEO:
    #     time.sleep(1)
    
    control_tello_thread = threading.Thread(target=control_tello)
    control_tello_thread.daemon = True
    control_tello_thread.start()

    try:
        test_cv_loop()
    except KeyboardInterrupt:
        print("Ctrl c")

def test_cv_loop():
    fno=0

    #time.sleep(3)
    while run:
        now_frame = tello.get_frame()
        if now_frame is None:
            time.sleep(0.1)
            continue
        
        fno += 1

        if now_frame is None or now_frame.size == 0:
            print(type(now_frame))
            continue
        #     return 0
        # R -> B
        # G -> G
        # B -> R
        now_frame = cv2.cvtColor(now_frame, cv2.COLOR_RGB2BGR)
        # now_frame: numpy.ndarray

        # ドローンの情報をOpenCVに表示
        tello_status = tello.stat
        cv2.putText(now_frame, text="battery: "+str(tello_status["bat"]), org=(20, 50), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 255, 0), thickness=1, lineType=cv2.LINE_4)
        cv2.putText(now_frame, text="height: "+str(tello_status["h"]), org=(20, 70), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 255, 0), thickness=1, lineType=cv2.LINE_4)
        cv2.putText(now_frame, text="time: "+str(tello_status["time"]), org=(20, 90), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 255, 0), thickness=1, lineType=cv2.LINE_4)
        cv2.putText(now_frame, text="pitch: "+str(tello_status["pitch"]), org=(20, 110), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 255, 0), thickness=1, lineType=cv2.LINE_4)
        cv2.putText(now_frame, text="roll: "+str(tello_status["roll"]), org=(20, 130), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 255, 0), thickness=1, lineType=cv2.LINE_4)
        cv2.putText(now_frame, text="yaw: "+str(tello_status["yaw"]), org=(20, 150), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 255, 0), thickness=1, lineType=cv2.LINE_4)
        

        # スティックの入力情報と実行するコマンドをOpenCVに表示        
        if tello.cmd_now != None:
            cmd_now = tello.cmd_now
        else:
            cmd_now = "none"

        cv2.putText(now_frame, text="LSTICK X: "+str(left_stick_x), org=(550, 580), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 0, 255), thickness=2, lineType=cv2.LINE_4)
        cv2.putText(now_frame, text="LSTICK Y: "+str(left_stick_y), org=(550, 610), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 0, 255), thickness=2, lineType=cv2.LINE_4)
        cv2.putText(now_frame, text="RIGHT X: "+str(right_stick_x), org=(550, 640), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 0, 255), thickness=2, lineType=cv2.LINE_4)
        cv2.putText(now_frame, text="RIGHT Y"+str(right_stick_y), org=(550, 670), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 0, 255), thickness=2, lineType=cv2.LINE_4)
        
        cv2.putText(now_frame, text="command: "+cmd_sc, org=(550, 700), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0, 0, 255), thickness=2, lineType=cv2.LINE_4)
        # org: 文字の描画領域の左下の頂点の
        # thickness: 文字の太さ
        # lineType: 文字描画
        cv2.imshow("color", now_frame)
        # waitKeyがなければなぜかウィンドウに画像が表示されない
        key = cv2.waitKey(1)
        #if key == 0:
        #    break
        #time.sleep(1)

def control_tello():
    global cmd_sc
    global right_stick_x
    global right_stick_y
    global left_stick_x
    global left_stick_y

    pygame.init()
    pygame.joystick.init()

    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print("ジョイスティックの名前:", joystick.get_name())
    except:
        print("ジョイスティックが接続されていない")

    operation = False

    t0 = time.time()

    try:
        print("hogehgoe")
        while run:
            for event in pygame.event.get():
                if event.type == JOYBUTTONDOWN or event.type == KEYDOWN or event.type == JOYAXISMOTION:
                    operation = True

                    if joystick.get_button(START) or (event.type == KEYDOWN and event.key == K_w):# 離陸
                        cmd_sc = "takeoff"
                    elif joystick.get_button(BACK) or (event.type == KEYDOWN and event.key == K_s):# 着陸
                        cmd_sc = "land"
                    elif joystick.get_button(Y_BUTTON) or (event.type == KEYDOWN and event.key == K_j):# 上方向
                        cmd_sc = "rc 0 0 40 0"
                    elif joystick.get_button(A_BUTTON) or (event.type == KEYDOWN and event.key == K_l):# 下方向
                        cmd_sc = "rc 0 0 -40 0"
                    elif joystick.get_button(X_BUTTON):# X -> 左方向
                        cmd_sc = "rc -40 0 0 0"
                    elif joystick.get_button(B_BUTTON):# B -> 右方向
                        cmd_sc = "rc 40 0 0 0"
                    elif joystick.get_button(LB_BUTTON):# LB -> 左旋回
                        cmd_sc = "rc 0 0 0 -50"
                    elif joystick.get_button(RB_BUTTON):# RB -> 右旋回
                        cmd_sc = "rc 0 0 0 50"
                        
                    print(cmd_sc)

                    # 右スティックの操作 -> 縦: 前後移動 横: 左右移動
                    right_stick_x = int(joystick.get_axis(R_STICK_X) * 50)                    
                    right_stick_y = int(-1 * joystick.get_axis(R_STICK_Y) * 50)


                    left_stick_x = int(joystick.get_axis(L_STICK_X) * 50)
                    left_stick_y = int(joystick.get_axis(L_STICK_Y) * 50)

                    #print("\nx: ", stick_x)
                    # y は上方向に傾けるとマイナスの値になるので　x -1をする 
                    #print("y: ", stick_y)

                    if (right_stick_x < -20 or right_stick_x > 20) or (right_stick_y < -20 or right_stick_y > 20):
                        cmd_sc = 'rc %s %s %s %s'%(right_stick_x, right_stick_y, 0, 0)
                        print(cmd_sc)
                    
                    if (left_stick_x < -20 or left_stick_x > 20) or (left_stick_y < -20 or left_stick_y > 20):
                        cmd_sc = 'rc %s %s %s %s'%(0, 0, right_stick_y, right_stick_x)
                        print(cmd_sc)


                    if cmd_sc != "":
                        tello.put_command(cmd_sc)
                    pygame.event.pump()

            time.sleep(0.5)


    except( KeyboardInterrupt, SystemExit ):
        print("SIGINTを検知")

if __name__ == '__main__':
    main()
