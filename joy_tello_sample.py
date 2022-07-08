from tello import Tello
import sys
from datetime import datetime
import time

def main():
    tello = Tello()

    tello.send_command("command")

    try:
        while True:
            time.sleep(1)
            print("\n")
            print("1: takeoff")
            print("2: land")
            print("3: battery?")
            print("4: height?")
            print("commandを入力してENTER")
            command = input(">> ")
            time.sleep(1)

            if command == "1":
                command = "takeoff"
            elif command == "2":
                command = "land"
            elif command == "3":
                command = "battery?"
            elif command == "4":
                command = "height?"
            else:
                print("\nover")
                break

            print(command)
            
            tello.send_command(command)
    except( KeyboardInterrupt, SystemExit ):
        print("SIGINTを検知")


if __name__ == '__main__':
    main()
