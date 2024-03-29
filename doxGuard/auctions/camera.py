from __future__ import division
import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os
import base64

import re
import sys

from google.cloud import speech
# from google.cloud.speech import types
import pyaudio
from six.moves import queue


########################
## JRF
## VideoRecorder and AudioRecorder are two classes based on openCV and pyaudio, respectively.
## By using multithreading these two classes allow to record simultaneously video and audio.
## ffmpeg is used for muxing the two signals
## A timer loop is used to control the frame rate of the video recording. This timer as well as
## the final encoding rate can be adjusted according to camera capabilities
##

########################
## Usage:
##
## numpy, PyAudio and Wave need to be installed
## install openCV, make sure the file cv2.pyd is located in the same folder as the other libraries
## install ffmpeg and make sure the ffmpeg .exe is in the working directory
##
##
## start_AVrecording(filename) # function to start the recording
## stop_AVrecording(filename)  # "" ... to stop it
##
##
########################


class VideoRecorder:

    # Video class based on openCV
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    # Video starts being recorded
    def get_frame(self):
        ret, video_frame = self.video.read()
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces_list = find_faces(video_frame, face_cascade)
        blurred = blur_faces(video_frame, faces_list)
        # run video_frame through blurring system
        success, image = cv2.imencode(".jpg", video_frame)
        if success:
            return image.tobytes()

    # Finishes the video recording therefore the thread too
    def stop(self):
        if self.open:
            self.open = False
            self.video.release()
            cv2.destroyAllWindows()

        else:
            pass

    # Launches the video recording function using a thread
    def start(self):
        video_thread = threading.Thread(target=self.get_frame)
        video_thread.start()


def find_faces(frame, face_cascade):
    faces_coord = face_cascade.detectMultiScale(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    return faces_coord

def blur_faces(frame, faces):
    for (x, y, w, h) in faces:
        if y < 2:
            y = 2
        if x < 2:
            x = 2
        if y + h >= frame.shape[0] - 2:
            h = frame.shape[0] - y - 3
        if x + w >= frame.shape[1] - 2:
            w = frame.shape[1] - x - 3
        y -= 2
        h += 2
        x -= 2
        w += 2

        ROI = frame[y:y + h, x:x + w]

        blur = cv2.GaussianBlur(ROI, (299, 299), 0)
        frame[y:y + h, x:x + w] = blur
        # frame[y:y+h, x:x+w] = cv2.resize(cv2.resize(ROI, (h//10, w//10), interpolation=cv2.INTER_LINEAR), (h, w), interpolation=cv2.INTER_NEAREST)

    return frame


# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self):
        self._rate = RATE
        self._chunk = CHUNK
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

