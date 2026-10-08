import json
import time
import serial

SERIAL_PORT = "/dev/ttyTHS1"
BAUD = 115200

BASE_SPEED = 0.20
SPIN_SPEED = 0.25
MAX_SPEED = 0.35

SECONDS_PER_FOOT = 1.2
SECONDS_PER_90_TURN = 1.75

ser = serial.Serial(SERIAL_PORT, BAUD, timeout=0.1)


def send_motors(left, right):
    command = {
        "T": 1,
        "L": round(left, 3),
        "R": round(right, 3)
    }

    ser.write((json.dumps(command) + "\n").encode())


def clamp(speed):
    return max(-MAX_SPEED, min(MAX_SPEED, speed))


def drive(left, right):
    send_motors(clamp(left), clamp(right))


def stop():
    send_motors(0.0, 0.0)


def move_forward(feet):
    print(f"Moving forward {feet} ft")

    drive(BASE_SPEED, BASE_SPEED)

    time.sleep(SECONDS_PER_FOOT * feet)

    stop()

    time.sleep(0.2)


def turn_left_90():
    print("Turning left 90 degrees")

    drive(-SPIN_SPEED, SPIN_SPEED)

    time.sleep(SECONDS_PER_90_TURN)

    stop()

    time.sleep(0.2)


def turn_right_90():
    print("Turning right 90 degrees")

    drive(SPIN_SPEED, -SPIN_SPEED)

    time.sleep(SECONDS_PER_90_TURN)

    stop()

    time.sleep(0.2)


def test_one_tile():
    move_forward(1)

def test_short_forward():
    print("Short forward test...")
    drive(BASE_SPEED, BASE_SPEED)
    time.sleep(0.25)
    stop()
    print("Test complete.")

if __name__ == "__main__":
    print("1 = SHORT forward test")
    print("2 = move forward 1 tile")
    print("3 = turn left 90 degrees")
    print("4 = turn right 90 degrees")
    print("0 = stop")

    choice = input("Enter command: ")

    if choice == "1":
        test_short_forward()

    elif choice == "2":
        test_one_tile()

    elif choice == "3":
        turn_left_90()

    elif choice == "4":
        turn_right_90()

    elif choice == "0":
        stop()

    else:
        print("Invalid command")