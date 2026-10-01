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
## [ChangeLog for Rover] — 2026-09-21
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
