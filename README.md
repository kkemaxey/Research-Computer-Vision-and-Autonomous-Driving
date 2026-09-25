# Research: Computer Vision and Autonomous Driving
 
An NSF-funded undergraduate research project at Morehouse College exploring vision-based autonomous navigation on a small ground rover. The rover (a Waveshare UGV with an NVIDIA Jetson Orin Nano) follows a taped course using classical color-based lane detection, and uses a YOLO model to recognize turn signs and react to them.
 
**Team:** Kanayo Egwuekwe-Maxey ([@kkemaxey](https://github.com/kkemaxey)), Brent Foxworth ([@BrentF10](https://github.com/BrentF10)), Jonathan Ross ([@JonRoss7](https://github.com/JonRoss7))\
**Advisor:** Prof. Abdelkrim Brania, Department of Mathematics\
**Funding:** National Science Foundation 2306300\
**Status:** Active, Fall 2026\
 
---
 
## Research Goals
 
This semester builds on the baseline system handed off by Omar White-Evans (Class of 2026). Our current goals are:
 
1. **Right-line following.** Change the controller so the rover drives on the right green line instead of centering between both lines.
2. **Smooth Turning.** Once turns are reliable and accurate, replace the current stop-and-spin maneuvers with smoother, continuous turns.

Weekly progress, experiments, and results are logged in [`CHANGELOG.md`](CHANGELOG.md).
 
---
 
## How the System Works
 
**Lane detection (no ML).** Each camera frame is converted to HSV and thresholded for green. The script samples a strip of floor just ahead of the rover and finds the position of each green line from the center of mass of its pixels. The steering error is smoothed and fed into a proportional differential-drive controller.
 
**Sign detection (YOLO).** A YOLO11n model, exported to TensorRT for the Jetson, detects left-turn, right-turn, and U-turn signs. When a confident detection is large enough in the frame (a rough proxy for distance), the rover performs the matching turn, then goes back to lane following.
 
**Motor control.** Wheel speeds are sent as JSON commands over the Jetson's serial port (`/dev/ttyTHS1`) to the rover's motor controller.
 
---
 
## Hardware and Software
 
| Component | Details |
|---|---|
| Rover | Waveshare UGV, three Panasonic NCR18650B batteries |
| Compute | NVIDIA Jetson Orin Nano, JetPack 7.2 |
| Model | Ultralytics YOLO11n → TensorRT `.engine` |
| Annotation | CVAT (SAM2/SAM3-assisted) |
| Base software | [waveshareteam/ugv_jetson](https://github.com/waveshareteam/ugv_jetson) (ROS 2 + Flask control app) |
 
---
 
## Repository Structure
 
```
.
├── autonomous_movement_hsv.py   # Main autonomy script (lane keeping + sign turns)
├── train_val_split.py           # Splits collected photos into train/validation sets
├── requirements-jetson.txt      # Dependencies for the Jetson (read notes inside)
├── requirements-pc.txt          # Dependencies for the training machine
├── CHANGELOG.md                 # Weekly research log
├── docs/
│   └── SETUP_GUIDE.md           # Full assembly, data, and training guide
└── images/                      # Figures used in the setup guide
```
 
---
 
## Quick Start
 
For a new rover, follow [`docs/SETUP_GUIDE.md`](docs/SETUP_GUIDE.md) from the beginning. With an already assembled rover and a trained `best.engine` on the Jetson:
 
```bash
# 1. Calibrate the green threshold (motors stay off in this mode)
python3 autonomous_movement_hsv.py --tune
 
# 2. Paste the best range into GREEN_LOWER / GREEN_UPPER, then drive
python3 autonomous_movement_hsv.py
```
 
To retrain the sign model on the training machine:
 
```bash
yolo detect train data=data.yaml model=yolo11n.pt epochs=100 imgsz=640 batch=16 device=0
yolo export model=path/to/best.pt format=engine device=0   # run this on the Jetson
```
 
---
 
## Project History

The rover platform, data pipeline, baseline autonomy script, and setup guide were developed by **Omar White-Evans** (Computer Science, Class of 2026) under Prof. Brania. **Kanayo Egwuekwe-Maxey** (Computer Science, Class of 2027) contributed to data collection, code structure, ideation, and testing, and verified the setup guide before handoff. Omar's original guide is preserved in [`docs/SETUP_GUIDE.md`](docs/SETUP_GUIDE.md).
