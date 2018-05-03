# Author : Carl Perez
# Date : 22 Feb 2018
# Title : Execute Motion Capture
# Description : Activates motion detection script and sends it back
# to the host for conversion into a usable .avi for further analysis

import paramiko
import sys
import time
import os
import subprocess

# initialize parameters to pass through paramiko
pi_server = "cybervision001"
pi_username = "pi"

pi_capture_location1 = "/home/pi/cyber_vision/after_motion1.h264"
pi_capture_location2 = "/home/pi/cyber_vision/before_motion1.h264"
pi_capture_location3 = "/home/pi/cyber_vision/after_motion2.h264"
pi_capture_location4 = "/home/pi/cyber_vision/before_motion2.h264"

local_capture_location1 = "./raw_video/after_motion1.h264"
local_capture_location2 = "./raw_video/before_motion1.h264"
local_capture_location3 = "./raw_video/after_motion2.h264"
local_capture_location4 = "./raw_video/before_motion2.h264"

local_avi_location = "./avi_video/motion_detected_" + time.strftime("%Y%m%d-%H%M") + ".avi"
execute_motion_capture = "cd ~/cyber_vision/ && python motion_capture.py"
delete_motion_capture = "cd ~/cyber_vision/ && rm motion_capture.py"

# initialize SSH client and keys for passwordless entry globally
ssh = paramiko.SSHClient()
ssh.load_host_keys("./.ssh/cyber_vision_known_hosts")
print("Connecting to " + pi_server + " with the user : " + pi_username + "...")
try :
    ssh.connect(pi_server, username=pi_username)
except paramiko.ssh_exception.SSHException as e:
    print "SSH Error : " + str(e)
    sys.exit(1)
print("Connection succesful.")

# create buffer reading function to deal with async paramiko SSH execution
def buffer_reader(p_buffer):
    line_buffer = ""
    while not p_buffer.channel.exit_status_ready():
        line_buffer += p_buffer.read(1)
        if line_buffer.endswith('\n'):
            yield line_buffer
            line_buffer = ''

# execute any command remotely on pi
def remote_execute(command) :
    print("Executing " + command + " on " + pi_server + " as " + pi_username + "...")
    pi_stdin, pi_stdout, pi_stderr = ssh.exec_command(execute_motion_capture, get_pty=True)
    for line in buffer_reader(pi_stdout):
        print line
    print("Execution finished.")

# download any file remotely from pi
def remote_sftp_download(local_path, remote_path) :
    print("Downloading " + remote_path + " from remote to local " + local_path + "...")
    sftp = ssh.open_sftp()
    sftp.get(remote_path, local_path)
    sftp.close()
    print("Successfully downloaded requested file.")

# convert raw video data into a usable avi for analysis by matlab/simulink
def convert_raw_to_avi(raw, avi) :
    print("Converting raw " + raw + " to usable " + avi + "...")
    command_string = "ffmpeg -i " + raw + " -c:v copy -an " + avi
    subprocess.check_output(
        command_string,
        stderr=subprocess.STDOUT,
        shell=True)
    print("Conversion succesful.")

# actual execution
remote_execute(execute_motion_capture)

time.sleep(5)

remote_sftp_download(local_capture_location1, pi_capture_location1)
remote_sftp_download(local_capture_location2, pi_capture_location2)
remote_sftp_download(local_capture_location3, pi_capture_location3)
remote_sftp_download(local_capture_location4, pi_capture_location4)

convert_raw_to_avi(local_capture_location1, "./avi_video/before_motion1.avi")
convert_raw_to_avi(local_capture_location2, "./avi_video/before_motion2.avi")
convert_raw_to_avi(local_capture_location3, "./avi_video/after_motion1.avi")
convert_raw_to_avi(local_capture_location4, "./avi_video/after_motion2.avi")

concat_cmd_1 = "ffmpeg -f concat -safe 0 -i full_motion1.txt -c copy ./avi_video/full_motion2.avi"
concat_cmd_2 = "ffmpeg -f concat -safe 0 -i full_motion2.txt -c copy ./avi_video/full_motion1.avi"

concat_cmd_1 = "ffmpeg -f concat -safe 0 -i full_motion1.txt -c copy ./avi_video/full_motion2.avi"
concat_cmd_2 = "ffmpeg -f concat -safe 0 -i full_motion2.txt -c copy ./avi_video/full_motion1.avi"

subprocess.check_output(
    concat_cmd_1,
    stderr=subprocess.STDOUT,
    shell=True)
subprocess.check_output(
    concat_cmd_2,
    stderr=subprocess.STDOUT,
    shell=True)

# have to close here to use ftp properly, will neaten up later
ssh.close()
