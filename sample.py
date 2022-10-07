from tello import Tello
import sys
import time
import threading
from pygame.locals import *
import pygame

run = True

tello = Tello()
pygame.init()

def main():
    tello.send_command("command")
#     control_tello_thread = threading.Thread(target=control_tello)
#     get_info_thread = threading.Thread(target=get_info)

#     get_info_thread.setDaemon(True)
#     #control_tello_thread.setDaemon(True)

#     #get_info_thread.start()
#     #control_tello_thread.start()

#     tello.send_command("command")

#     while True:
#         time.sleep(1)

def control_tello():
    #tello = Tello()

    #tello.send_command("command")

    try:
        while run:
            print("\n")
            print("1: takeoff")
            print("2: land")
            print("3: battery?")
            print("4: height?")
            #print("5: up 10cm")
            print("commandを入力してENTER")
            command = input(">> ")

            if command == "1":
                command = "takeoff"
            elif command == "2":
                command = "land"
            elif command == "3":
                command = "battery?"
            elif command == "4":
                command = "height?"
            #elif command == "5":
            #    command = "up "
            else:
                print("\nover")
                break

            print(command)
            
            tello.send_command(command)
    except( KeyboardInterrupt, SystemExit ):
        print("SIGINTを検知")

def get_info():
    while run:
        tello.send_command("battery?")
        tello.send_command("height?")
        print(time.time())
        print("\033[8A")

if __name__ == '__main__':
    main()
