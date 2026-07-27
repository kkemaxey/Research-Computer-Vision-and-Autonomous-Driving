""" Rover autonomy: HSV green-line lane keeping + YOLO turn signs.

Lane detection uses a green colour mask (no ML): the frame is converted to HSV,
thresholded for green, and a horizontal strip near the bottom of the frame is
sampled to find where the left and right lines sit.  The midpoint of those two
is where the rover should be.  YOLO is still used, but only for turn signs.

Two modes:
    python3 autonomous_movement_hsv.py --tune    calibrate the green range and exit
    python3 autonomous_movement_hsv.py           drive

Run --tune first, with the rover parked where it can see both lines.  It writes
tune_*.png masks you can scp over; paste the winning range into GREEN_LOWER /
GREEN_UPPER below.  Tune mode never opens the serial port, so the motors cannot
move while you calibrate.
"""
import json
import sys
import time
import cv2
import numpy as np
import serial
from ultralytics import YOLO
from enum import Enum

MODEL_PATH = "best.engine"
CAM_INDEX = 0
SERIAL_PORT = "/dev/ttyTHS1"
BAUD = 115200

FRAME_W = 640
FRAME_H = 480

# class IDs from data.yaml (Lane/3 unused now -- HSV handles lanes)
CLS_RIGHT = 0
CLS_LEFT = 1
CLS_UTURN = 2
CLS_LANE = 3

SIGN_CONF = 0.40

# ---- HSV green thresholds -- SET THESE FROM --tune OUTPUT
# Hue in OpenCV is 0-179.  Green sits around 35-85.
# Keep hue narrow (that's what makes it "green"); keep S and V wide so shadow
# and glare on the same line still match.
GREEN_LOWER = np.array([35, 60, 40])
GREEN_UPPER = np.array([85, 255, 255])

# ---- region of interest: the strip of floor just ahead of the rover
ROI_TOP_FRAC = 0.60      # start 60% down the frame
ROI_BOT_FRAC = 0.95      # stop near the bottom edge
MIN_PIXELS = 120         # fewer green pixels than this on a side = "no line there"

# speed
BASE_SPEED = 0.20
SEARCH_SPEED = 0.12
MAX_SPEED = 0.35
SPIN_SPEED = 0.25

# lane keeping
TURN_GAIN = 0.35
SMOOTHING = 0.7
ONE_LINE_NUDGE = 0.25

# sign trigger + maneuver
TURN_TRIGGER = 0.25
SPIN_SECONDS = 3.5       # <-- CALIBRATE
TURN_COOLDOWN = 8.0

TUNE_MODE = "--tune" in sys.argv


class objectType(Enum):
    RIGHTTURN = 0
    LEFTTURN = 1
    UTURN = 2
    NONE = 4


class roverState(Enum):
    LANE_FOLLOWING = 0
    SEARCHING = 1


# small kernel used to knock out speckle noise in the mask
KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))


# ----------------------------------------------------------------- lanes (HSV)
def greenMask(frame, lower=None, upper=None):
    """BGR frame -> binary mask, white where green."""
    lower = GREEN_LOWER if lower is None else lower
    upper = GREEN_UPPER if upper is None else upper
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    # MORPH_OPEN = erode then dilate: removes isolated specks without
    # shrinking the real lines much.
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL)


def centroidX(strip):
    """Weighted mean x of the white pixels in a mask strip, or None if too few.
    Summing down the columns collapses the strip to a 1-D profile of 'how much
    green is in each column', then we take its centre of mass."""
    col_sums = strip.sum(axis=0).astype(np.float64)   # one value per column
    total = col_sums.sum()
    if total < MIN_PIXELS * 255:          # mask pixels are 255, not 1
        return None
    xs = np.arange(strip.shape[1], dtype=np.float64)
    return float((xs * col_sums).sum() / total)


def getLaneCentersHSV(frame, roi_top, roi_bot, frame_w):
    """Return (left_x, right_x); either may be None if that line isn't visible."""
    mask = greenMask(frame)
    roi = mask[roi_top:roi_bot, :]         # the strip of floor just ahead
    mid = frame_w // 2

    left_x = centroidX(roi[:, :mid])                       # search left half
    right_x = centroidX(roi[:, mid:])
    if right_x is not None:
        right_x += mid                     # shift back into full-frame coords

    return left_x, right_x


def laneError(left_x, right_x, frame_w):
    """Steering error in -1..+1.  Negative = lane centre is left of frame
    centre -> steer left.  None = no line at all."""
    if left_x is not None and right_x is not None:
        lane_center = (left_x + right_x) / 2
        return (lane_center - frame_w / 2) / (frame_w / 2)

    if left_x is not None:
        return +ONE_LINE_NUDGE             # only left line -> drifted left -> steer right
    if right_x is not None:
        return -ONE_LINE_NUDGE             # only right line -> steer left

    return None


# ----------------------------------------------------------------- tune mode
def run_tune(cap, frame_w, frame_h, roi_top, roi_bot):
    """Grab a frame, report the hues actually present, try candidate green
    ranges, and write each mask to a PNG.  No serial, no motors."""
    # throw away the first few frames; webcams need a moment to auto-expose
    for _ in range(10):
        cap.read()

    ok, frame = cap.read()
    if not ok:
        raise SystemExit("failed to grab a frame")

    cv2.imwrite("tune_00_frame.png", frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # what hue is actually in your green line?  Sample the ROI and report the
    # most common hues among reasonably-saturated pixels.
    roi_hsv = hsv[roi_top:roi_bot, :]
    hues = roi_hsv[:, :, 0][roi_hsv[:, :, 1] > 60]
    if hues.size:
        counts = np.bincount(hues, minlength=180)
        print("most common hues in ROI (hue: pixel count):")
        for hue in counts.argsort()[::-1][:5]:
            print(f"  {hue:3d}: {counts[hue]}")
        print("  (green is usually 35-85; if your line's hue isn't in that band,")
        print("   widen GREEN_LOWER/GREEN_UPPER to bracket the numbers above)")
    else:
        print("no saturated pixels found - is anything colourful in view?")

    candidates = {
        "narrow": (np.array([45, 80, 60]), np.array([75, 255, 255])),
        "default": (np.array([35, 60, 40]), np.array([85, 255, 255])),
        "wide": (np.array([30, 40, 30]), np.array([95, 255, 255])),
    }

    mid = frame_w // 2
    for name, (lo, hi) in candidates.items():
        mask = greenMask(frame, lo, hi)
        roi = mask[roi_top:roi_bot, :]
        left_px = int(roi[:, :mid].sum() / 255)
        right_px = int(roi[:, mid:].sum() / 255)
        print(f"{name:8s} lower={lo.tolist()} upper={hi.tolist()}  "
              f"ROI green px: left={left_px} right={right_px}")
        cv2.imwrite(f"tune_{name}.png", mask)

    print("\nwrote tune_*.png - scp them over and look at the masks.")
    print("You want: both lines solid white, floor black, minimal speckle.")
    print("Then paste the winning range into GREEN_LOWER / GREEN_UPPER.")


# ----------------------------------------------------------------- motors
def make_motor_funcs(ser):
    """Build the motor helpers around an open serial port.  Only called when
    actually driving, so tune mode never touches /dev/ttyTHS1."""

    def send_motors(left, right):
        cmd = {"T": 1, "L": round(left, 3), "R": round(right, 3)}
        ser.write((json.dumps(cmd) + "\n").encode())

    def clamp(v):
        return max(-MAX_SPEED, min(MAX_SPEED, v))

    def drive(left, right):
        send_motors(clamp(left), clamp(right))

    def stop():
        send_motors(0.0, 0.0)

    def spin_in_place(direction=1, spin_duration=SPIN_SECONDS):
        print(f"SPINNING: direction={direction} duration={spin_duration}")
        stop()
        time.sleep(0.1)
        drive(SPIN_SPEED * direction, -SPIN_SPEED * direction)
        time.sleep(spin_duration)
        stop()
        time.sleep(0.2)

    return drive, stop, spin_in_place


# ----------------------------------------------------------------- signs (YOLO)
def getBoxHeightFrac(corners_of_box, frame_h):
    _, y1, _, y2 = corners_of_box
    return abs(y1 - y2) / frame_h


def checkDetectedSigns(frame_boxes, frame_h):
    for b in frame_boxes[0].boxes:
        cls = int(b.cls[0])
        conf = float(b.conf[0])
        if cls == CLS_LANE:
            continue                       # lanes come from HSV now
        if conf > SIGN_CONF and getBoxHeightFrac(b.xyxy[0], frame_h) >= TURN_TRIGGER:
            match cls:
                case 0:
                    return objectType.RIGHTTURN
                case 1:
                    return objectType.LEFTTURN
                case 2:
                    return objectType.UTURN
    return objectType.NONE


# ----------------------------------------------------------------- main
def main():
    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        raise SystemExit(f"camera {CAM_INDEX} did not open - check ls /dev/video*")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)

    # cap.set is a request, not a promise -- read back what we actually got
    frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"actual frame size: {frame_w}x{frame_h}")

    roi_top = int(frame_h * ROI_TOP_FRAC)
    roi_bot = int(frame_h * ROI_BOT_FRAC)

    # --- tune mode: calibrate and exit, no serial, no motors ---------
    if TUNE_MODE:
        try:
            run_tune(cap, frame_w, frame_h, roi_top, roi_bot)
        finally:
            cap.release()
        return

    # --- drive mode --------------------------------------------------
    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=0.1)
    drive, stop, spin_in_place = make_motor_funcs(ser)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter("rover_view.mp4", fourcc, 20.0, (frame_w, frame_h))
    model = YOLO(MODEL_PATH, task="detect")

    state = roverState.SEARCHING
    smoothed_error = 0.0
    last_turn = -1e9

    try:
        while True:
            success, frame = cap.read()
            if not success:
                continue

            # --- 1. turn signs take priority (YOLO) -------------------
            frame_boxes = model(frame, verbose=False)
            writer.write(frame_boxes[0].plot())

            detected_sign = checkDetectedSigns(frame_boxes, frame_h)
            if detected_sign != objectType.NONE and (time.time() - last_turn) > TURN_COOLDOWN:
                match detected_sign:
                    case objectType.RIGHTTURN:
                        spin_in_place(direction=+1, spin_duration=SPIN_SECONDS / 2)
                    case objectType.LEFTTURN:
                        spin_in_place(direction=-1, spin_duration=SPIN_SECONDS / 2)
                    case objectType.UTURN:
                        spin_in_place(direction=+1, spin_duration=SPIN_SECONDS)
                last_turn = time.time()
                state = roverState.SEARCHING
                smoothed_error = 0.0
                continue

            # --- 2. lane keeping (HSV) --------------------------------
            left_x, right_x = getLaneCentersHSV(frame, roi_top, roi_bot, frame_w)
            error = laneError(left_x, right_x, frame_w)

            if error is None:
                if state != roverState.SEARCHING:
                    print("lanes lost -> SEARCHING")
                    state = roverState.SEARCHING
                drive(SEARCH_SPEED, SEARCH_SPEED)
                continue

            if state == roverState.SEARCHING:
                print(f"lanes found (L={left_x} R={right_x}) -> LANE_FOLLOWING")
                state = roverState.LANE_FOLLOWING

            smoothed_error = SMOOTHING * smoothed_error + (1 - SMOOTHING) * error

            left = BASE_SPEED + TURN_GAIN * smoothed_error
            right = BASE_SPEED - TURN_GAIN * smoothed_error
            drive(left, right)

    except KeyboardInterrupt:
        pass
    finally:
        stop()
        time.sleep(0.2)
        stop()
        ser.close()
        cap.release()
        writer.release()


if __name__ == "__main__":
    main()
