import io
import picamera
import motion_detect
import ConfigParser
import time
from PIL import Image

prior_image = None
file_number = 1
total_video_length = 0
first_video_started_at = 0
last_video_started_at = 0
last_video_ended_at = time.time()

conf_raw = ConfigParser.ConfigParser()
conf_raw.read('config.ini')
config = {section: dict(conf_raw.items(section)) for section in conf_raw.sections()}

def detect_motion(camera):
    global prior_image
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg', use_video_port=True)
    stream.seek(0)
    if prior_image is None:
        prior_image = Image.open(stream)
        return False
    current_image = Image.open(stream)
    # Compare current_image to prior_image to detect motion. This is left
    # as an exercise for the reader!
    is_there_motion = motion_detect.detect(
        current_image,
        prior_image,
        int(config['motion_detection']['threshold']),
        float(config['motion_detection']['minimum_area'])
    )
    # Once motion detection is done, make the current image the prior one
    prior_image = current_image
    return is_there_motion


def write_before(stream, filename):
    # Write the entire content of the circular buffer to disk. No need to lock
    # the stream here as we're definitely not writing to it simultaneously
    with io.open(filename, 'wb') as output:
        for frame in stream.frames:
            if frame.header:
                stream.seek(frame.position)
                break
        while True:
            buf = stream.read1()
            if not buf:
                break
            output.write(buf)
    # Wipe the circular stream once we're done
    stream.seek(0)
    stream.truncate()


def process_motion(camera):
    global file_number
    global total_video_length
    global prior_image
    global first_video_started_at
    global last_video_ended_at

    stream = picamera.PiCameraCircularIO(
        camera, seconds=int(config['recording_settings']['margin']))
    camera.start_recording(stream, format='h264')
    try:
        while True:
            camera.wait_recording(
                int(config['motion_detection']['interval']))
            if detect_motion(camera):
                print('Motion detected.')
                last_video_started_at = time.time()

                if first_video_started_at == 0:
                    first_video_started_at = time.time()

                # split the stream
                camera.split_recording(
                    "motion_video%d.h264" % (file_number + 1))
                # Write the 10 seconds "before" motion to disk as well, and update the file number
                write_before(stream, "motion_video%d.h264" % file_number)
                file_number += 2
                current_length = total_video_length

                # Wait until motion is no longer detected, then split
                # recording back to the in-memory circular buffer
                while current_length < int(config['recording_settings']['maximum_chunk_length']) and detect_motion(camera):
                    current_length = total_video_length + time.time() - last_video_started_at
                    camera.wait_recording(
                        int(config['motion_detection']['interval']))

                print('Motion no longer detected.')
                last_video_ended_at = time.time()
                total_video_length += last_video_ended_at - last_video_started_at

                print("Total length of video stream: %ds" %
                      total_video_length)
                camera.split_recording(stream)

                if total_video_length >= int(config['recording_settings']['maximum_video_length']):
                    print("Maximum video length reached")
                    break

                if file_number / 2 > int(config['recording_settings']['maximum_chunk_count']):
                    print("Maximum chunk count reached")
                    break

                elif first_video_started_at > 0 and time.time() - first_video_started_at > int(config['recording_settings']['maximum_recording_time']):
                    print("Maximum recording time reached")
                    break
                elif last_video_ended_at > 0 and time.time() - last_video_ended_at > int(config['recording_settings']['maximum_idle_time']):
                    print("Maximum idle time reached")
                    break
    finally:
        camera.stop_recording()


if __name__ == '__main__':

    with picamera.PiCamera() as camera:
        camera.resolution = (
            int(config['camera_settings']['width']), int(config['camera_settings']['height']))
        process_motion(camera)
