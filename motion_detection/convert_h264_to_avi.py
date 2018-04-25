import sys
import time
import os
import subprocess

def convert_raw_to_avi(raw, avi) :
    print("Converting raw " + raw + " to usable " + avi + "...")
    command_string = "../ffmpeg/ffmpeg -i " + raw + " -c:v copy -an " + avi
    subprocess.check_output(
        command_string,
        stderr=subprocess.STDOUT,
        shell=True)
    print("Conversion succesful.")

convert_raw_to_avi("before_motion1.h264", "before_motion1.avi")
convert_raw_to_avi("before_motion2.h264", "before_motion2.avi")
convert_raw_to_avi("after_motion1.h264", "after_motion1.avi")
convert_raw_to_avi("after_motion2.h264", "after_motion2.avi")
