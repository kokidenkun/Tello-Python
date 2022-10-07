import time
from tello import Tello
import sys
import threading

def main():
    main_ctl_event = threading.Event()

    t1 = threading.Thread(target=get_time, args=(main_ctl_event,))
    t2 = threading.Thread(target=get_word, args=(main_ctl_event,))

    t1.start()
    t2.start()

def get_time(event):
    event.set()
    while True:
        event.wait()
        print(str(time.time()))
        print("\033[2A")
        time.sleep(2)

def get_word(event):
    word = input(">> ")
    print(word)
    event.clear()
    time.sleep(5)
    event.set()

if __name__ == "__main__":
    main()
