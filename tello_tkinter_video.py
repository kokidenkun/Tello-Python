import tello as tello
import tkinter
from tkinter import Toplevel, Scale
import threading
from PIL import Image
from PIL import ImageTk
import time

import sys
from pygame.locals import *
import pygame

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

pygame.init()
pygame.joystick.init()

try:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("ジョイスティックの名前:", joystick.get_name())
except:
    print("ジョイスティックが接続されていない")

screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("hogehoge")

class VideoUI:

    def __init__(self, tello, outputpath="./"):
        self.tello = tello
        self.outputpath = outputpath

        self.root = tkinter.Tk()
        self.root.wm_title("Tello")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        self.panel = None

        self.stopEvent = threading.Event()
        self.video_thread = threading.Thread(target=self.videoloop, args=())
        self.video_thread.start()

        self.sending_command_thread = threading.Thread(target=self._sendingCommand)

        self.control_tello_thread = threading.Thread(target=self.control_tello)
        self.control_tello_thread.daemon = True
        self.control_tello_thread.start()

    
    # 映像をTkinterのウィンドウに描画し続けるスレッド
    def videoloop(self):
        try:
            time.sleep(0.5)

            while True:            
                # self.tello.read ->
                self.frame = self.tello.read()
                if self.frame is None or self.frame.size == 0:
                    continue

                image = Image.fromarray(self.frame)

                self._updateGUIImage(image)
        
        except RuntimeError as e:
            print("caught a RuntimeError")

    def _updateGUIImage(self, image):
        image = ImageTk.PhotoImage(image)
        #print("hoge")

        if self.panel is None:
            self.panel = tkinter.Label(image=image)
            self.panel.image = image
            self.panel.pack(side="left", padx=10, pady=10)
        else:
            self.panel.configure(image=image)
            self.panel.image = image
    
    def _sendingCommand(self):
        while True:
            self.tello.send_command("command")
            time.sleep(5)
    
    def onClose(self):
        print("closing....")
        self.stopEvent.set()
        del self.tello
        self.root.quit()
        #pygame.quit()

    def control_tello():
        operation = False

        t0 = time.time()

        try:
            while run:
                screen.fill((0, 0, 0))
                for event in pygame.event.get():
                    if event.type == JOYBUTTONDOWN or event.type == KEYDOWN or event.type == JOYAXISMOTION:
                        operation = True

                        #print("something will happen")

                        if joystick.get_button(START) or (event.type == KEYDOWN and event.key == K_w):
                            print("takeoff")
                            self.tello.send_command("takeoff")
                        elif joystick.get_button(BACK) or (event.type == KEYDOWN and event.key == K_s):
                            print("land")
                            self.tello.send_command("land")
                        elif joystick.get_button(Y_BUTTON) or (event.type == KEYDOWN and event.key == K_j):# 上方向
                            self.tello.send_command("rc %s %s %s %s"%(0, 0, 20, 0))
                            print("up 20")
                        elif joystick.get_button(A_BUTTON) or (event.type == KEYDOWN and event.key == K_l):# 下方向
                            self.tello.send_command("rc %s %s %s %s"%(0, 0, -20, 0))
                            print("down 20")
                        elif joystick.get_button(X_BUTTON):# X -> 左方向
                            self.tello.send_command("rc %s %s %s %s"%(-20, 0, 0, 0))
                            print("left 20")
                        elif joystick.get_button(B_BUTTON):# B -> 右方向
                            self.tello.send_command("rc %s %s %s %s"%(20, 0, 0, 0))
                            print("right 20")
                        elif joystick.get_button(LB_BUTTON):# LB -> 左旋回
                            self.tello.send_command("rc %s %s %s %s"%(0, 0, 0, -50))
                            print("left yaw 50")
                        elif joystick.get_button(RB_BUTTON):# RB -> 右旋回
                            self.tello.send_command("rc %s %s %s %s"%(0, 0, 0, 50))
                            print("right yaw 50")

                        elif joystick.get_button(LOGICOOL):
                            self.tello.send_command("time?")
                    
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

                time.sleep(0.1)

                if operation:
                    operation = False
            #else:
                #tello.send_command("battery?")
                #print("time: ", time.time()-t0, "\n")
            
                time.sleep(0.5)


        except( KeyboardInterrupt, SystemExit ):
            print("SIGINTを検知")


def main():

    drone = tello.Tello('', 8889)
    vui = VideoUI(drone)

    vui.root.mainloop()

if __name__ == "__main__":
    main()
