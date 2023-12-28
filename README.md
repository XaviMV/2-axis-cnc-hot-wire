# 2-Axis-CNC-Hot-Wire-Foam-Cutter
## Overview
This project combines 3D printing, Arduino, and Python to create a 2-axis CNC hot wire foam cutter. The system allows users to calibrate the CNC machine, sketch paths for the cutter to follow, and execute those paths. This README provides an overview of the project, installation instructions, and usage guidelines.

## Usage

An Arduino board must always be connected to the computer and flashed with the code inside the "code_for_arduino" folder. The communication from the computer to the Arduino is taken from https://github.com/mkals/Arduino-Python3-Command-API.

After executing main.py a terminal will open with 3 different options aside from the exit function.

* __Calibration:__

This option will open a PyGame window where the CNC machine can be calibrated. The following variables will be extracted from the calibration: maximum and minimum PWM of each servo, maximum servo height (minimum height will always be 0) and the direction of each stepper. After each calibration, this information will be stored as a file inside the "data" folder, and it will be read before path sketching and path execution.

<p align="center">
  <img src="https://github.com/XaviMV/2-axis-cnc-hot-wire/assets/70759474/dcc6d435-585b-4a8a-aafb-f96d468ac331" width="800">
</p>

* __Path Sketching:__

This will also open a PyGame window where the first image found in the main folder will be shown, in case the objective is to trace it. The maximum height of the drawing will be limited by the maximum servo height set at the calibration step. The first point of the path will be at the bottom left of the canvas, and each click in the canvas will generate the next point. After finishing the path and giving it a name it will be stored in the "data" directory, inside the "created_paths" folder, where it will be accessible in the path execution step.

https://github.com/XaviMV/2-axis-cnc-hot-wire/assets/70759474/a3b7c521-1f75-4c85-97c9-5fa9a94c6b80

* __Path execution:__

This time no PyGame window will be opened, the name of a previously created path will be asked and after verifying its existence, it will be executed on the CNC.

## Demo

I have bought some nichrome wire to finish the CNC but I am still waiting for it to arrive, when I get it I will upload a video of the foam cutting process.

## Requirements

Python 3.9

pip packages:
  
> opencv-python

> arduino-python3

> pygame

> numpy

> customtkinter

> CTkMessagebox

## 3D Prints and Hardware

Information about the 3D files, prints and hardware used in the building of the CNC is inside the folder "3D prints".
