# Motion Detection
This is python based motion detection and recording algorithm based on the Sum of Absolute Differences.

# Requirements + Dependencies
### Hardware Requirements
* PC capable of basic video conversion
* Raspberry PI 3 Model B
  * Ethernet cable to connect the laptop and PI
  * 5V 2.4A power supply
* Raspberry Camera Module v2

### Software Requirements
* Windows 7+ or Linux (preferably one running the apt package manager)
* Python 2.7
* A SSH client capable of generating SSH keys (Linux SSH prefered, PuTTY is possible)
* A video player capable of viewing .avi files (raw H.264 is a plus, [VLC](https://www.videolan.org/vlc/index.html "VLC Download") is a good choice)
### Dependencies
* FFmpeg (Download [here.](https://www.ffmpeg.org/download.html "FFmpeg Download"))
* PiCamera 1.10 (Installation instructions [here.](https://picamera.readthedocs.io/en/release-1.10/install2.html "Pi Camera Download"))
* Paramiko (Installation instructions [here.](http://www.paramiko.org/installing.html "Paramiko Installation"))
* SciPy and Numpy (Should both be preinstalled on any Linux system, but if not, follow [these instructions.](https://scipy.org/install.html "SciPy Installation"))
###### NOTE: Software Requirements and Dependencies are required on both the Pi and your PC

### Executing the Program
1. Create an SSH key between the Raspberry Pi and your PC. Follow [these instructions](https://www.raspberrypi.org/documentation/remote-access/ssh/passwordless.md "SSH Key Instructions") and be sure to make the key passwordless, otherwise the program may not execute as intended.
2. After creating the SSH key, navigate to **/path/to/CyberVision/motion_detection** and run the following command:
``` bash
ssh -oHostKeyAlgorithms='ssh-rsa' -o  UserKnownHostsFile=./.ssh/cyber_vision_known_hosts pi@<hostname of your pi>
```
3. Move the **motion_capture.py** script to the **/home/pi/cyber_vision/** on  your Raspberry Pi. This can be done via SCP or SFTP.
4. Ensure that the *pi_server* and *pi_username* inside **execute_motion_capture.py** match the login you use to SSH into your Raspberry, the executor script will fail to execute the motion capture script.
5. Execute **execute_motion_capture.py** with Python.
6. View your time stamped .avi file in **/path/to/CyberVision/motion_detection/avi_video** and see if it properly detections motion.
7. If it does not, tinker with the *camera_settings* and *motion_sensitivity* dictionaries in **motion_capture.py**. (preferably on the Pi, but you can edit it locally and re-move it to the Pi).



### Licensing for motion_capture.py
###### Copyright 2013-2015 Dave Jones
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
