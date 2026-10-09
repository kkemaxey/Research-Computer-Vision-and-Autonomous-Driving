# Changelog — Autonomous UGV Rover Research

All notable changes to this project are documented here.
Entries are newest-first. Each entry covers one week of work.

**Team:** Kanayo Egwuekwe-Maxey, Brent Foxworth, Jonathan Ross
**GitHub:** [@kkemaxey](https://github.com/kkemaxey), [@BrentF10](https://github.com/BrentF10), [@JonRoss7](https://github.com/JonRoss7)
**Advisor:** Prof. Abdelkrim Brania
**Format:** Based on [Keep a Changelog](https://keepachangelog.com), extended for research tracking.

## Entry Template

~~~markdown
## [Short Title] — YYYY-MM-DD
**Author(s):** [who did the work]
**Goal:** [one sentence: what this week was trying to achieve]

### Code
- Added / Changed / Fixed / Removed: [description]

### Model & Dataset *(if changed)*
- [model version, dataset changes, training config, metrics]

### Parameters *(if changed)*
- [parameter]: [old] → [new] — [reason]

### Test Results *(if tested)*
- [what was tested, outcome, link to video/logs]

### Known Issues
- [new issues found, or inherited issues resolved this week]

### Next Steps
- [plan for next week]
~~~

--- 

## (ChangeLog for Rover) — 2026-10-09
**Brent Foxworth and Jonathan Ross:** Continued work on the rover movement code by creating a separate movement testing script and testing basic forward movement on the rover.

**Goal:** Continue developing the basic movement commands for the rover and begin testing whether the rover can accurately move across the 1 ft by 1 ft course tiles.

### Code
- Added `movement_test.py` as a separate file so testing could continue without changing the unfinished `basic_movement.py` file.
- Added basic commands for moving forward, stopping, turning left, and turning right.
- Added a short forward movement test and a menu for testing individual movement commands.
- Used `/dev/ttyTHS1` at 115200 baud for communication with the rover.

### Model & Dataset *(if changed)*
- No changes

### Parameters *(if changed)*
- `BASE_SPEED = 0.25`
- `SPIN_SPEED = 0.25`
- `MAX_SPEED = 0.35`
- `SECONDS_PER_FOOT = 1.4`
- `SECONDS_PER_90_LEFT = 1.25`
- `SECONDS_PER_90_RIGHT = 1.34`

### Test Results *(if tested)*
- Successfully tested the short forward movement command and confirmed that the rover moves forward correctly.
- Tested the 1-tile forward command using the current timing value.
- The rover moved forward and successfully stopped in the tile right in front of it.
- The left and right turns for the rover are inconsistent (Overturns and Under turns are frequent).

### Known Issues
- Left and right 90 degree turns sometimes over or under turn (I believe this could be due to how the weight is distributed on the rover/friction)
- Movement is currently based on timing, so distance may be affected by battery level and floor conditions.

### Next Steps
- Calibrate the forward movement timing so the rover travels one full 1 ft tile.
- Test and calibrate the left and right 90 degree turns.
- Continue building the basic movement commands needed for the rover to complete the course.



## (ChangeLog for Rover) — 2026-10-02
**Jonathan Ross and Brent Foxworth:** Started writing the code for the basic movements that we established and possibly fixed the rover's connection issues to the Wi-FI

**Goal:** Either get some progress done with the code for the Rover or start defining how we'll get the accuracy metrics for the rover.

### Code
- Still modifying the code right now, not actively done yet. Hopefully, will try to push the code sometime next week.

### Model & Dataset *(if changed)*
- No changes

### Parameters *(if changed)*
- No changes

### Test Results *(if tested)*
- No changes

### Known Issues
- Previous issue: WI-FI connection (potentially solved now) and the new SSD/OS having to be reinstalled for the rover.
- Current Issue: Flask overloading for running the app.py file 

### Next Steps
- Finish the basic_movements.py code file so we can try to get a test run of the rover going through the course using our commands
- Elaborate more on the accuracy metrics and see how we can formally define them.



## (ChangeLog for Rover) — 2026-09-21

**Jonathan Ross and Brent FoxWorth:** We were troubleshooting WI-FI issues with the rover, developed a basic algorithm for the rover to follow on the course, and captured a couple photos on the rover.

**Goal:** Try to access into the Rover and begin to understand the code/take miscellaneous pictures with the rover after attaining access to it.

### Code
- No coded was added or changed this week

### Model & Dataset *(if changed)*
- No Change

### Parameters *(if changed)*
- No Change

### Test Results *(if tested)*
- No test Results

### Known Issues
- Flask overloading,Rover WI-FI sometimes dropping or not being to directly SSH into the rover,and previous SSD had to be removed to reinstall OS into new SSD.

### Next Steps
- Either continue working on the algorithm, possibly fixing the Flask overloading issue when the camera freezes, and figure out the accuracy metrics for the rover.



## Baseline (handoff from Omar White-Evans) — 2026-07-27
**Goal:** Record the state of the project at handoff.

### Code
- `autonomous_movement_hsv.py`: HSV lane-centering between two green lines + YOLO sign detection with timed turns.
- `train_val_split.py`: 80/20 split, seed 42.

### Model & Dataset
- YOLO11n, 100 epochs, 640px → `rover_v3`, exported to TensorRT.
- ~150 images per sign class + lane labels, annotated in CVAT.

### Known Issues (inherited)
- Lane class (id 3) is trained but unused at runtime.
- Segmentation labels are exported, but the model is trained with `yolo detect`.
- Turns are time-based and sensitive to battery charge and floor friction.
- CVAT tutorial links in the README are placeholders.

### Next Steps
- Implement right-line following (see SETUP_GUIDE "Your Task").
- Update the SETUP_GUIDE with accurate tutorial links.
