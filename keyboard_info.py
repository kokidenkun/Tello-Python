from tello import Tello
import sys
import time
import threading
from pygame.locals import *
import pygame

run = True

tello = Tello()
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("hogehoge")

def main():
    control_tello_thread = threading.Thread(target=control_tello)
    get_info_thread = threading.Thread(target=get_info)

    tello.send_command("command")

    control_tello_thread.daemon = True
    control_tello_thread.start()

    get_info_thread.daemon = True
    get_info_thread.start()


    while run:
        time.sleep(1)


def control_tello():
    #tello = Tello()

    #tello.send_command("command")
    operation = False
    t0 = time.time()
    try:
        while run:
            screen.fill((0, 0, 0))
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    operation = True
                    print("keydown")
                    if event.key == K_w:
                        tello.send_command("takeoff")
                        print("takeoff")
                    elif event.key == K_s:
                        tello.send_command("land")
                        print("land")
                    elif event.key == K_j:
                        tello.send_command("rc 0, 0, 20, 0")
                        print("up 20")
                    elif event.key == K_l:
                        tello.send_command("rc 0, 0, -20, 0")
                        print("down 20")
            if operation:
                operation = False
            else:
                tello.send_command("battery?")
                # tello.send_command("height?")
                print('time: ', time.time()-t0)
                print("")
            time.sleep(0.01)

    except( KeyboardInterrupt, SystemExit ):
        print("SIGINTを検知")

def get_info():
    while run:
#        tello.send_command("battery?")
#        tello.send_command("height?")
#        print(time.time())
        time.sleep(3)
#        print("")
        

if __name__ == '__main__':
    main()
