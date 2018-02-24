# Author : Dave Jones (with minor edits by Carl Perez)
# Date : 22 Feb 2018
# Title : Motion Capture
# Description : Takes video stream, and when the vectors between
# multiple images reach a specified thresold, hold past 5 seconds of recording
# record for 30 second and save the raw video file in the working directory.
# NOTE : MUST BE EXECUTED ON A RASPBERRY PI

from __future__ import division

import picamera
import numpy as np
import time

# Set up motion data
motion_dtype = np.dtype([
    ('x', 'i1'),
    ('y', 'i1'),
    ('sad', 'u2'),
])

# make params of video recording/motion detection easier to manipulate to
# enable quicker calibration
# TO DO
# Enable automated calibration
# Incorporate SAD
camera_settings = {'width': 640, 'height': 480,'fps': 30, 'record_time': 5}
motion_sensitivity = {'max number of vectors': 17, 'max magnitude of vectors': 86}

# create motion detector class
class my_motion_detector(object):

    def __init__(self, camera):
        width, height = camera.resolution
        self.cols = (width + 15) // 16
        self.cols += 1  # there's always an extra column
        self.rows = (height + 15) // 16

    # Load the motion data from the string to a numpy array
    # Then, apply vectors between differences of images
    # If there's >15 vectors with >80 magnitude, then there's motion
    def write(self, s):
        data = np.fromstring(s, dtype=motion_dtype)
        data = data.reshape((self.rows, self.cols))
        data = np.sqrt(
        np.square(data['x'].astype(np.float)) +np.square(data['y'].astype(np.float))
        ).clip(0, 255).astype(np.uint8)
        if (data > motion_sensitivity['max magnitude of vectors']).sum() > motion_sensitivity['max number of vectors']:
            print("Motion detected at " + time.strftime("%Y-%m-%d-%H:%M:%S") + "!")
        return len(s)

# Record motion data to our custom output object
# This will record upon the first instance of motion
# i.e. Multiple instances of motion will not reset the video stream
# Don't be alarmed by multiple print messages
with picamera.PiCamera() as camera:
    camera.resolution = (camera_settings['width'], camera_settings['height'])
    camera.framerate = camera_settings['fps']
    camera.start_recording(
    './motion_detected.h264', format='h264',
    motion_output=my_motion_detector(camera)
    )
    camera.wait_recording(camera_settings['record_time'])
    camera.stop_recording()
