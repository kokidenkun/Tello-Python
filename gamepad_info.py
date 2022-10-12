from tello import Tello
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

R_STICK_X = 3
R_STICK_Y = 4

tello = Tello(video=True) # ビデオ配信有効
# tello = Tello(video=False)  # ビデオ配信無効

pygame.init()
pygame.joystick.init()

try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("ジョイスティックの名前:", joystick.get_name())
except:
    print("ジョイスティックが接続されていない")

# ここはいらない
#screen = pygame.display.set_mode((400, 400))
#pygame.display.set_caption("hogehoge")

def main():
    get_info_thread_inst = threading.Thread(target=get_info_thread)

    control_tello_thread = threading.Thread(target=control_tello)
    control_tello_thread.daemon = True
    control_tello_thread.start()

    get_info_thread_inst.daemon = True
    get_info_thread_inst.start()

    # while not VIDEO:
    #     time.sleep(1)

    try:
        while True:
            test_cv_loop()
    except KeyboardInterrupt:
        print("Ctrl c")


def test_cv_loop():
    fno=0

    #time.sleep(3)
    while run:
        now_frame = tello.read()
        if now_frame is None:
            time.sleep(0.1)
            continue

        #print(fno, now_frame)
        fno += 1

        if now_frame is None or now_frame.size == 0:
            print(type(now_frame))
            continue
        #     return 0
        # R -> B
        # G -> G
        # B -> R
        now_frame = cv2.cvtColor(now_frame, cv2.COLOR_RGB2BGR)
        #print(type(now_frame))
        # now_frame: numpy.ndarray
        # img = cv2.imread(now_frame)
        cv2.putText(now_frame, text="battery: "+str(bat), org=(20, 50), 
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1.0, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_4)
        # org: 文字の描画領域の左下の頂点の
        # thickness: 文字の太さ
        # lineType: 文字病が
        cv2.imshow("color", now_frame)
        # waitKeyがなければなぜかウィンドウに画像が表示されない
        key = cv2.waitKey(1)
        #if key == 0:
        #    break
        #time.sleep(1)



def control_tello():
    operation = False

    t0 = time.time()

    try:
        while run:
            for event in pygame.event.get():
                if event.type == JOYBUTTONDOWN or event.type == KEYDOWN or event.type == JOYAXISMOTION:
                    operation = True

                    #print("something will happen")

                    # if joystick.get_button(LOGICOOL):
                    #     tello.send_command("time?")


                    if joystick.get_button(START) or (event.type == KEYDOWN and event.key == K_w):
                        print("takeoff")
                        tello.send_command("takeoff")
                    elif joystick.get_button(BACK) or (event.type == KEYDOWN and event.key == K_s):
                        print("land")
                        tello.send_command("land")
                    elif joystick.get_button(Y_BUTTON) or (event.type == KEYDOWN and event.key == K_j):# 上方向
                        tello.send_command("rc %s %s %s %s"%(0, 0, 40, 0))
                        print("up 20")
                    elif joystick.get_button(A_BUTTON) or (event.type == KEYDOWN and event.key == K_l):# 下方向
                        tello.send_command("rc %s %s %s %s"%(0, 0, -40, 0))
                        print("down 20")
                    elif joystick.get_button(X_BUTTON):# X -> 左方向
                        tello.send_command("rc %s %s %s %s"%(-20, 0, 0, 0))
                        print("left 20")
                    elif joystick.get_button(B_BUTTON):# B -> 右方向
                        tello.send_command("rc %s %s %s %s"%(20, 0, 0, 0))
                        print("right 20")
                    elif joystick.get_button(LB_BUTTON):# LB -> 左旋回
                        tello.send_command("rc %s %s %s %s"%(0, 0, 0, -50))
                        print("left yaw 50")
                    elif joystick.get_button(RB_BUTTON):# RB -> 右旋回
                        tello.send_command("rc %s %s %s %s"%(0, 0, 0, 50))
                        print("right yaw 50")

                    elif joystick.get_button(LOGICOOL):
                        print(tello.send_command("time?"))
                    
                    # else:
                    #     print("nothing happen.")

                    #stick_x = int(joystick.get_axis(R_STICK_X) * 100)                    
                    #stick_y = int(-1 * joystick.get_axis(R_STICK_Y) * 100)

                    #print("\nx: ", stick_x)
                    # y は上方向に傾けるとマイナスの値になるので　x -1をする 
                    #print("y: ", stick_y)

                    # if stick_x < -20 or stick_x > 20:
                    #     print("rc %s %s %s %s"%(stick_x / 2, 0, 0, 0))
                    #     tello.send_command('rc %s %s %s %s'%(stick_x / 2, 0, 0, 0))

                    # if stick_y < -20 or stick_y > 20:
                    #     print("rc %s %s %s %s"%(0, 0, stick_y / 2, 0))
                    #     tello.send_command('rc %s %s %s %s'%(0, 0, stick_y / 2, 0))
                    # if (stick_x < -20 or stick_x > 20) or (stick_y < -20 or stick_y > 20):
                    #     print("rc %s %s %s %s"%(stick_x / 2, 0, stick_y, 0))
                    #     tello.send_command('rc %s %s %s %s'%(stick_x / 2, 0, stick_y / 2, 0))
                    
                    pygame.event.pump()

            time.sleep(0.001)

            if operation:
                operation = False
            #else:
                #tello.send_command("battery?")
                #print("time: ", time.time()-t0, "\n")
        


    except( KeyboardInterrupt, SystemExit ):
        print("SIGINTを検知")   

def get_info_thread():
    global bat
    while run:
        bat = tello.send_command("battery?")
        print('TIME:', time.time(),  'BAT:', bat)
        
        # height = tello.send_command("height?")
        # print('TIME:', time.time(),  'HEIGHT:', height)
        time.sleep(0.5)
        print("")
        

if __name__ == '__main__':
    main()
