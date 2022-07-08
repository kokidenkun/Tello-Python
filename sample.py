from tello import Tello
import sys
import time

def main():
    tello = Tello()

    tello.send_command("command")

    try:
        while True:
            print("\n")
            print("1: takeoff")
            print("2: land")
            print("3: battery?")
            print("4: height?")
            print("5: up 10cm")
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
            elif command == "5":
                command = "up "
            else:
                print("\nover")
                break

            print(command)
            
            tello.send_command(command)
    except( KeyboardInterrupt, SystemExit ):
        print("SIGINTを検知")


if __name__ == '__main__':
    main()
