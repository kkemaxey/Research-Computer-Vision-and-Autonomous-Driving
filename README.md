# Autonomous UGV Rover — Assembly, Data Pipeline & Self-Driving Guide

An end-to-end guide for building a Waveshare UGV rover on an NVIDIA Jetson Orin Nano, collecting and annotating a training dataset, and training a YOLO model to drive the rover autonomously along a taped course.

**Author:** Omar Michael White-Evans — Computer Science, Class of 2026
**Advisor:** Professor Abdelkrim Brania — Professor of Mathematics
**Last updated:** July 27, 2026


---

## Table of Contents

- [Part 1: Rover Assembly and ROS 2 Installation](#part-1-rover-assembly-and-ros-2-installation)
  - [1. Choose a Storage Device and Flash Jetson Linux](#1-choose-a-storage-device-and-flash-jetson-linux)
  - [2. Boot Jetson Linux on the Jetson Orin Nano](#2-boot-jetson-linux-on-the-jetson-orin-nano)
  - [3. Set Up User Profile, Wi-Fi, and USB-C Connection](#3-set-up-user-profile-wi-fi-and-usb-c-connection)
  - [4. Install ROS 2 on the Jetson Orin Nano](#4-install-ros-2-on-the-jetson-orin-nano)
  - [5. Attach the Jetson Board to the UGV Rover](#5-attach-the-jetson-board-to-the-ugv-rover)
- [Part 2: Data Collection and Annotation](#part-2-data-collection-and-annotation)
  - [1. SSH into the Jetson and Run the ROS 2 Web App](#1-ssh-into-the-jetson-and-run-the-ros-2-web-app)
  - [2. Taking Pictures with the Rover](#2-taking-pictures-with-the-rover)
  - [3. Annotation with CVAT](#3-annotation-with-cvat)
- [Part 3: Model Training and Autonomous Movement](#part-3-model-training-and-autonomous-movement)
  - [1. Set Up the data.yaml File](#1-set-up-the-datayaml-file)
  - [2. Transport the Model to the Jetson and Optimize to a `.engine` File](#2-transport-the-model-to-the-jetson-and-optimize-to-a-engine-file)
  - [3. Run the Autonomy Script](#3-run-the-autonomy-script)
- [Your Task](#your-task)

---

# Part 1: Rover Assembly and ROS 2 Installation

## 1. Choose a Storage Device and Flash Jetson Linux

You can flash Jetson Linux (Ubuntu) onto the Jetson Orin Nano using either of two storage devices:

- A 64 GB UHS-1 (or larger) microSD card
- An NVMe SSD

### microSD Method

**Materials**

- 64 GB or larger microSD card
- Flashing software on your PC
- 16 GB or larger flash drive

**Steps**

1. Download the NVIDIA JetPack 7.2 ISO image file ([step 2 on the Jetson user guide](#)).
2. Download flashing software such as [balenaEtcher](#) to write OS images onto the flash drive.
3. Insert the USB flash drive into your PC. Using balenaEtcher (or another flashing tool), flash the ISO file onto the flash drive, then eject it from your computer.
4. With the flash drive now holding the image file, insert it into one of the USB ports on the Jetson, then insert the microSD card into the Jetson's microSD card slot.

> **⚠️ Important:** JetPack 7.2 does **not** support SD card images. **Do not** flash the JetPack 7.2 ISO directly to the microSD from your PC. You must use a USB flash drive as described in the microSD steps above.

### NVMe SSD Method

Unless you have an NVMe adapter that connects to your computer (allowing you to flash the SSD with an ISO image directly), the steps are essentially the same as the microSD method. The key difference is that you must install the NVMe card on the Jetson Orin Nano ([instructions here](#)) instead of inserting a microSD card.

---

## 2. Boot Jetson Linux on the Jetson Orin Nano

**Things you'll need**

- A monitor (the ones in the Math Department's computer lab work well)
- A DisplayPort-to-HDMI cable (the Jetson uses a DisplayPort connection for GUI output)
- A USB keyboard
- A USB mouse

**Steps**

1. Connect the DisplayPort end to the Jetson and the HDMI end to the monitor. Connect the USB ends of the mouse, keyboard, and flash drive to the Jetson's USB ports. The Jetson ships with a DC barrel-jack power cord — after connecting everything else, plug it into the DC power jack on the Jetson, and the Jetson should turn on.
2. Once the Jetson powers on (indicated by the green light next to the USB-C port), repeatedly press the **Esc** key to access the Unified Extensible Firmware Interface (UEFI). From here, select the inserted flash drive as the boot device.

---

## 3. Set Up User Profile, Wi-Fi, and USB-C Connection

Once the OS boots successfully, you'll be prompted to create your user profile. **Write down the password you create and store it somewhere safe.**

### a) Connect to Wi-Fi

If you're in the Math lab, connect to **"MyResNet-5G"** using its password. (This is the network used for this project; network names may change at Morehouse.)

1. Click the **Show Applications** icon and type `settings` in the search bar.
2. Open the **Settings** application and connect to the network.

### b) Enable Auto-Connect

Open the Jetson's terminal and run:

```bash
# Check the name of the network you're connected to
nmcli connection show

# Tell the Jetson to reconnect to this network on every boot
nmcli connection modify 'MyResNet-5G' connection.autoconnect yes
```

With auto-connect enabled, the Jetson rejoins the same network whenever it boots, so you can easily SSH into it from a PC on the same network.

### c) Enable USB-C (ECM) Connection on macOS *(optional, but recommended)*

By default, the Jetson uses the Remote Network Driver Interface Specification (RNDIS) when connected over USB-C. This protocol is **not supported on macOS**. To change it:

1. Open a terminal on the Jetson (`Ctrl + Alt + T`).
2. Edit the USB device-mode config:
   ```bash
   sudo vim /opt/nvidia/l4t-usb-device-mode/nv-l4t-usb-device-mode-config.sh
   ```
   ([Learn vim here](#).)
3. Change `RNDIS = 1` to `RNDIS = 0`, and make sure `ECM = 1`.

### d) Assign a Static IP to Mitigate SSH Issues *(optional, but may be needed)*

I ran into frequent problems SSHing into the Jetson at one point. My theory is that it was related to Morehouse's network implementing DHCP (Dynamic Host Configuration Protocol) lease-alignment delays. Assigning a static IP to the Jetson bypassed those delays. My steps:

```bash
sudo nmcli connection modify "MyResNet-5G" ipv4.method "auto" ipv4.addresses "11.21.55.150/16"
sudo nmcli connection up "YOUR_WIFI_NAME"
```

---

## 4. Install ROS 2 on the Jetson Orin Nano

> *Only required for non-Waveshare Jetson Orin Nano boards.*

1. With the monitor, keyboard, and mouse still connected, open a terminal and `git clone` [this repo](#) into your home directory. (Run `cd ~` first if you're unsure where your home directory is.)
2. Disconnect the monitor, keyboard, and mouse from the Jetson, then move on to the next step.

---

## 5. Attach the Jetson Board to the UGV Rover

> **⚠️ Disclaimer:** If you bought the official Jetson Orin Nano reference board ([link](#)), it was **not** designed to be assembled onto the UGV rover. You need the "Jetson Orin Nano 4GB" kit that ships with the UGV rover kit for the screws to be compatible with rover assembly. That said, the steps below describe how I assembled the reference board onto the UGV rover.

**Assembly with the Jetson Orin Nano from the kit:** follow [Waveshare's assembly video](#).

**Assembly with an outside board (Jetson Nano):** if the D500 Lidar and OAK-D-Lite camera are not installed, watch the first minute of [Waveshare's assembly video](#), then return to these directions.

In case the videos are unavailable, here is the written assembly procedure.

### Step 1 — Install the Batteries

First install the batteries into the Jetson Orin Nano. The UGV rover supports three 3.7 V 18650 lithium batteries. Not every lithium battery will fit into the rover ([more information on battery sizes here](#)). The batteries we used were the **Panasonic NCR18650B**.

Unscrew the four screws on the bottom of the rover to open the chassis compartment where the batteries are housed.

<p align="center">
  <img src="images/01-rover-battery-compartment.jpg" width="480" alt="Bottom of the rover with the four chassis screws circled">
  <br>
  <em>The four chassis screws (circled) on the bottom of the rover.</em>
</p>

Install the three lithium batteries into the rover.

> **⚠️ Critical:** Install the batteries facing the correct polarity. If you install them backwards, you will burn out the power module when the charging cord is connected or when the rover is turned on.

<p align="center">
  <img src="images/02-battery-orientation.jpg" width="420" alt="An 18650 battery held to show its negative and positive ends">
  <br>
  <em>Battery orientation — note the negative and positive ends.</em>
</p>

### Step 2 — Open the Rover Housing

After installing the batteries, unscrew the four screws on the rover and place them somewhere you won't lose them.

<p align="center">
  <img src="images/03-rover-top-screws.jpg" width="480" alt="Top of the rover with four screws circled">
  <br>
  <em>Unscrew these four screws (circled).</em>
</p>

Next, take the rover's top off and unscrew the four silver pillars beneath it. Again, keep them somewhere safe. The pillars look like this:

<p align="center">
  <img src="images/04-silver-pillars.jpg" width="360" alt="One of the silver standoff pillars from the rover">
  <br>
  <em>One of the four silver pillars.</em>
</p>

### Step 3 — Connect the Rover to the Jetson Board

Connect the following from the rover to the Jetson board:

**Clip the UGV rover's network antenna cords onto the Jetson network card** (on the bottom of the Jetson).

<p align="center">
  <img src="images/05-jetson-antenna-cords.jpg" width="420" alt="Attaching the rover's antenna cords to the Jetson network card">
  <br>
  <em>Clip the antenna cords onto the Jetson's network card.</em>
</p>

<p align="center">
  <img src="images/06-wifi-card-clip.jpg" width="480" alt="Close-up of the Wi-Fi card showing where to clip the antenna">
  <br>
  <em>Close-up of the clip points on the Wi-Fi card.</em>
</p>

Place the Jetson on the short silver pillars.

<p align="center">
  <img src="images/07-jetson-on-pillars.jpg" width="480" alt="Jetson board seated on the short silver pillars, mounting points circled">
  <br>
  <em>Seat the Jetson on the short silver pillars (mounting points circled).</em>
</p>

<p align="center">
  <img src="images/08-jetson-ribbon-cable.jpg" width="420" alt="Holding the ribbon cable near the Jetson before connecting">
  <br>
  <em>Prepare the ribbon cable for connection.</em>
</p>

**Connect the double-row cables to the Jetson main-unit pins.**

> **⚠️ Important:** Connect the DuPont jumper cables to the **first five sets of pins**, starting from the set closest to the USB-C port.

<p align="center">
  <img src="images/09-double-row-cables.jpg" width="420" alt="DuPont jumper cables connected to the first five sets of Jetson pins">
  <br>
  <em>DuPont jumper cables on the first five sets of pins (closest to the USB-C port).</em>
</p>

**Plug all three USB cables from the rover into the Jetson's USB ports:**

- Audio driver board
- USB camera
- Type-A connector to the OAK-D-Lite camera

<p align="center">
  <img src="images/10-usb-cables-top.jpg" width="480" alt="Three USB cables plugged into the Jetson, viewed from above">
  <br>
  <em>All three USB connections (circled), top view.</em>
</p>

<p align="center">
  <img src="images/11-usb-cables-side.jpg" width="420" alt="Three USB cables plugged into the Jetson, side view">
  <br>
  <em>Side view of the USB connections.</em>
</p>

### Step 4 — Power On the Rover

Connect the DC power cable (the one with the red and black wires) and the DC charging cable to the rover when powering it on for the first time. Press the power button to turn the rover on.

<p align="center">
  <img src="images/12-power-button-charging-port.jpg" width="420" alt="Rover with the power button and charging port labeled">
  <br>
  <em>Power button and charging port.</em>
</p>

A **green light** indicates that the Jetson Orin Nano is powered on.

<p align="center">
  <img src="images/13-green-light-on.jpg" width="480" alt="Green light indicating the Jetson Orin Nano is powered on">
  <br>
  <em>The green light means the Jetson Orin Nano is on.</em>
</p>

This is what you should see on the rover's OLED screen:

<p align="center">
  <img src="images/14-oled-screen-off.jpg" width="360" alt="The rover's OLED status screen at startup">
  <br>
  <em>The rover's OLED status screen.</em>
</p>

### ✅ Checkpoint

At this point you should have:

- ROS 2 installed on the Jetson
- The Waveshare UGV rover assembled with the Jetson attached
- The rover and Jetson Orin Nano powering on when the power button is pressed

---

# Part 2: Data Collection and Annotation

## 1. SSH into the Jetson and Run the ROS 2 Web App

1. SSH into the Jetson from your PC:
   ```bash
   ssh username@username.local
   ```
2. Change into the `ugv_jetson` directory and run the app:
   ```bash
   cd ugv_jetson
   python3 app.py
   ```

You should see terminal output similar to this:

<p align="center">
  <img src="images/15-app-terminal-output.png" width="760" alt="Terminal output from running app.py, showing the Flask server URL">
  <br>
  <em>Expected terminal output from <code>app.py</code>.</em>
</p>

On the second-to-last line you should see a log entry such as **`Running on http://11.25.6.5:5000`**. This is the URL you enter into your browser to access the rover's control web page. The IP address (here, `11.25.6.5`) changes daily, but the port **`5000`** always stays the same.

### Reduce Web Page Choppiness (edit `os_info.py`)

Inside the `ugv_jetson` directory there is also an `os_info.py` file that needs modifying to reduce choppiness when controlling the rover. Open `os_info.py` in your editor of choice (vim or nano) and make the following changes.

**On line 21, change the `net_interface` member variable to `"wlP1p1s0"`:**

<p align="center">
  <img src="images/16-os-info-line21.png" width="480" alt="os_info.py line 21 with net_interface set to wlP1p1s0">
  <br>
  <em>Set <code>net_interface = "wlP1p1s0"</code> on line 21.</em>
</p>

**On lines 88 and 100, change the current value to `"enP8p1s0"`:**

<p align="center">
  <img src="images/17-os-info-lines88-100.png" width="620" alt="os_info.py lines 88 and 100 updated to enP8p1s0">
  <br>
  <em>Set the IP-address lookups on lines 88 and 100 to <code>"enP8p1s0"</code>.</em>
</p>

> **Why these changes matter:** The older values did not match the Jetson's network interfaces. This caused logging errors that (I believe) starved the video-feed and web-page processes, resulting in the web page constantly freezing.

The control web page looks like this:

<p align="center">
  <img src="images/18-control-webpage.png" width="760" alt="The rover control web page with camera feed and control panels">
  <br>
  <em>The rover control web page.</em>
</p>

Here's a [video of me interacting with the web page](#) — it's best viewed at 2× speed.

When ROS 2 is running, you'll see this on the OLED screen:

<p align="center">
  <img src="images/19-oled-ros2-running.jpg" width="360" alt="OLED screen state while ROS 2 is running">
  <br>
  <em>OLED screen while ROS 2 is running.</em>
</p>

---

## 2. Taking Pictures with the Rover

> **Note:** All pictures taken with the rover are stored in `ugv_jetson/templates/pictures`. All videos are stored in `ugv_jetson/templates/videos`.

**Goal:** Take roughly **150 pictures each** of the U-turn, right-turn, and left-turn signs. The track lanes should ideally appear in most of the pictures. It's important to photograph each sign from **different angles** — this helps the computer-vision model distinguish the signs when they're viewed from varying perspectives.

*[Google Drive link with example pictures — **TODO: add link**]*

Once the pictures have been taken, secure-copy (`scp`) the pictures directory from `ugv_jetson/templates/pictures` onto your PC:

```bash
scp username@username.local:~[location of directory] [directory to download to on PC]
```

---

## 3. Annotation with CVAT

1. Compress the pictures directory into a `.zip` file and upload it into your annotation software (we used **CVAT**). Here are two videos to get familiar with CVAT: [Video 1](#) and [Video 2](#).
2. Use the `train_val_split.py` script in the repo to split the pictures folder into `training_images` and `validation_images` folders.
3. Compress both the `training_images` and `validation_images` folders into separate zip files.
4. Create a project for the annotations in CVAT, and upload the two zip files as two separate **tasks** within that project.
5. Label the task containing the training images as **`train`** and the task containing the validation images as **`validation`**.

Here is a visual of what that looks like:

<p align="center">
  <img src="images/20-cvat-task-config.png" width="760" alt="CVAT project view showing the train/validation subset configuration">
  <br>
  <em>Configuring the <code>train</code> / <code>validation</code> subsets in CVAT.</em>
</p>

6. Annotate every photo, correctly labeling which objects are U-turns, right turns, left turns, or lanes.

> **Use the SAM2 or SAM3 model for annotation.** This creates a **mask shape**. When you draw lines around your object, it creates a **polyline shape** instead. For the *YOLO Ultralytics Segmentation 1.0* format, only shapes annotated with a **mask shape** or **polygon shape** will have a label created for them. If no label is created for an object, that object is treated as background.

7. After finishing annotations:
   1. Click the **Projects** tab in the top menu.
   2. Click the project containing your annotated images.
   3. Click the **Actions ⋮** button in the upper-right corner. You'll see a menu like this:

<p align="center">
  <img src="images/21-cvat-export-dialog.png" width="480" alt="CVAT 'Export task as a dataset' dialog with 'Save images' toggled on">
  <br>
  <em>The export dialog — make sure <strong>Save images</strong> is switched on.</em>
</p>

   4. Under **Export format**, select **YOLO Ultralytics Segmentation 1.0**.
   5. Switch on **Save images** — this is very important, as it's what creates the image folder in the export.
   6. Under **Custom name**, give the export zip file a name.
   7. Click **OK**.
   8. You should see a confirmation message:

<p align="center">
  <img src="images/22-cvat-export-started.png" width="480" alt="CVAT 'Dataset export started' notification">
  <br>
  <em>The "Dataset export started" confirmation.</em>
</p>

   9. Under the **Requests** tab you should see your export loading. Once it's finished, right-click to download the export.
   10. Once downloaded, extract the zip file and move its contents into a new folder (preferably its own dedicated folder).

The contents of the exported zip file should look like this:

<p align="center">
  <img src="images/23-export-zip-contents.png" width="620" alt="Extracted export contents: labels, images, Validation.txt, Train.txt, data.yaml">
  <br>
  <em>Expected contents of the exported zip: <code>labels/</code>, <code>images/</code>, <code>Validation.txt</code>, <code>Train.txt</code>, and <code>data.yaml</code>.</em>
</p>

---

# Part 3: Model Training and Autonomous Movement

We'll use Ultralytics' [YOLO11n](#) base model and the YOLO CLI to train the model.

## 1. Set Up the data.yaml File

1. Your `data.yaml` file **must** contain the `train` and `val` keys. The values for these keys must be the **relative paths** of the training and validation images, relative to the `data.yaml` file itself.
2. Download the `yolo11n.pt` base model and make sure it's in the **same directory** as `data.yaml` ([download here](#)).

**This is the `data.yaml` file you should be given:**

<p align="center">
  <img src="images/24-data-yaml-given.png" width="620" alt="Original data.yaml with Train.txt and Validation.txt paths">
  <br>
  <em>The <code>data.yaml</code> file as provided.</em>
</p>

**Changes you need to make to the `data.yaml` file for training:**

<p align="center">
  <img src="images/25-data-yaml-training.png" width="480" alt="Modified data.yaml with train and val pointing to image folders">
  <br>
  <em>Update <code>train</code> and <code>val</code> to point to the image folders.</em>
</p>

The updated `data.yaml` should read:

```yaml
train: ./images/Train
val: ./images/Validation
names:
  0: RightTurnSignal
  1: LeftTurnSignal
  2: U-Turn
  3: Lane
path: .
```

> **⚠️** Failure to make these changes will result in:
> ```
> FileNotFoundError: Dataset not found ⚠️: {path to directory} not found
> ```

3. Run the following command in the directory containing `data.yaml` and `yolo11n.pt`:

```bash
yolo detect train data=data.yaml model=yolo11n.pt epochs=100 imgsz=640 batch=16 device=0 name=rover_v3
```

Once training is done, the model you want is stored at:

```
/home/[user account]/[location where training is done]/runs/detect/rover_v3-4/weights
```

`best.pt` is the model you want from the `weights` directory.

---

## 2. Transport the Model to the Jetson and Optimize to a `.engine` File

1. Make sure the `onnx` and `tensorrt` Python libraries are installed on the Jetson. (The `tensorrt` package takes a long time to download.)
2. Secure-copy the `best.pt` file from your PC to the Jetson, then run:
   ```bash
   yolo export model=path/to/best.pt format=engine device=0
   ```
   `best.engine` will be created in the directory where you ran the command, or wherever `best.pt` is located on the Jetson.

---

## 3. Run the Autonomy Script

1. Place the Jetson in front of the green lanes as shown below, and run `autonomous_movement_hsv.py` with the `--tune` flag:
   ```bash
   python3 autonomous_movement_hsv.py --tune
   ```
2. Then place the Jetson at the beginning of the course and run the following command to make it drive autonomously:
   ```bash
   python3 autonomous_movement_hsv.py
   ```

<p align="center">
  <img src="images/26-jetson-start-position.jpg" width="480" alt="Rover positioned at the start of the taped course beside a U-turn sign">
  <br>
  <em>The rover's start position on the course.</em>
</p>

[Video of the final product](#)

---

## Your Task

> I had Claude write most of the `autonomous_movement_hsv` script. The script was designed to make the robot drive **between** the two green lines.
>
> **Your job is to edit the current script (or write a new one) so the rover always drives on the *right* green line instead of between both green lines.**

The parts of `autonomous_movement_hsv` that I wrote:

- The `CheckDetectedBox` function
- The `object_type` enum class
- The case statements determining when to execute each type of turn (U-turn, left, and right)
