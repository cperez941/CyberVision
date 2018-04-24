import io
import picamera
import motion_detect
import ConfigParser
import io
from PIL import Image

prior_image = None


config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(io.BytesIO(sample_config))

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
            0,
            0.0002
        )
    # Once motion detection is done, make the current image the prior one
    prior_image = current_image
    return is_there_motion

def write_before(stream):
    # Write the entire content of the circular buffer to disk. No need to lock
    # the stream here as we're definitely not writing to it simultaneously
    with io.open('before.h264', 'wb') as output:
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
    stream = picamera.PiCameraCircularIO(camera, seconds=config['recording_settings']['margin'])
    camera.start_recording(stream, format='h264')
    try:
        while True:
            camera.wait_recording(5)
            if detect_motion(camera):
                # As soon as we detect motion, split the recording to record
                # the bits "after" motion
                camera.split_recording('after.h264')
                # While that's going, write the 10 seconds "before" motion to
                # disk as well, and wipe the circular stream
                write_video(stream)
                # Wait until motion is no longer detected, then split recording
                # back to the in-memory circular buffer
                while detect_motion(camera):
                    camera.wait_recording(5)
                camera.split_recording(stream)
    finally:
        camera.stop_recording()


if __name__ == '__main__':
    with picamera.PiCamera() as camera:
        camera.resolution = (1280, 720)
        process_motion(camera)
