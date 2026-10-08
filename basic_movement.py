import json
import time
import serial

SERIAL_PORT = "/dev/ttyTHS1"
BAUD = 115200

# Speed Settings 
BASE_SPEED = 0.20
SPIN_SPEED = 0.25
MAX_SPEED = 0.35

TIME_PER_SQUARE = 1.2
TIME_90_DEG_TURN = 1.75

ser = serial.Serial(SERIAL_PORT, BAUD, timeout = 0.1)

def send_motors(left, right):
    cmd = {"T": 1, "L": round(left, 3), "R": round(right,3)}
    ser.write((json.dumps(cmd) + "\n").encode())

def clamp(v: float) -> float:
    return max(-MAX_SPEED, min(MAX_SPEED, v))

def drive(left: float, right: float):
    send_motors(clamp(left), clamp(right))

def stop():
    send_motors(0.0, 0.0)


# ==========================================
# 2. PRIMITIVE ACTIONS
# ==========================================
def move_forward_squares(squares: int = 1):
    print(f"Moving forward {squares} square(s)...")
    drive(BASE_SPEED, BASE_SPEED)
    time.sleep(TIME_PER_SQUARE * squares)
    stop()
    time.sleep(0.1)

def spin_in_place(direction: int = 1, duration: float = TIME_90_DEG_TURN):
    """direction: +1 for right, -1 for left"""
    dir_str = "right" if direction > 0 else "left"
    print(f"Spinning {dir_str} for {duration}s...")
    stop()
    time.sleep(0.05)
    drive(SPIN_SPEED * direction, -SPIN_SPEED * direction)
    time.sleep(duration)
    stop()
    time.sleep(0.1)

def turn_left_90():
    spin_in_place(direction=-1, duration=TIME_90_DEG_TURN)

def turn_right_90():
    spin_in_place(direction=+1, duration=TIME_90_DEG_TURN)

# ==========================================
# 3. Whiteboard commands
# ==========================================
    
def execute_left_turn ():
    print ("Executing Left Turn routine...")
    move_forward_squares(2)
    turn_left_90()
    move_forward_squares(1)
    print ("Left Turn complete.")


def execute_right_turn ():
    print ("Executing Right Turn routine...")
    move_forward_squares(1)
    turn_right_90()
    move_forward_squares(1)
    print ("Right Turn complete.")

def execute_u_turn ():
    print ("Executing U-Turn rountine...")
    move_forward_squares(1)
    turn_left_90()
    move_forward_squares(1)
    turn_left_90()
    move_forward_squares(1)
    print("U-Turn complete.")

