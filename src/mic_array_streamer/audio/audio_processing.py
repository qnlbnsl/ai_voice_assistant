from multiprocessing import Queue
from collections import deque
import pyaudio
import wave
import numpy as np
import webrtcvad

# Libraries
from audio.beamforming import delay_and_sum, calculate_delays, estimate_doa_with_music

# Enums
from enums import (
    mic_positions,
    CHUNK,
    FORMAT,
    CHANNELS,
    RECORD_SECONDS,
    RATE,
    RECORD,
    NO_SPEECH_COUNT,
    NO_SPEECH_LIMIT,
    MIN_SPEECH_COUNT,
    MIN_SPEECH_TIME,
)

# Types
from webrtcvad import Vad

mic = pyaudio.PyAudio()


def initialize_audio(audio_queue: Queue):
    info = mic.get_host_api_info_by_index(0)
    num_devices = info.get("deviceCount")

    if num_devices is None:
        print("Could not fetch device count")
        exit()
    else:
        try:
            num_devices = int(num_devices)  # cast to int if possible
        except ValueError:
            print("Invalid device count received")
            exit()

        if num_devices < 1:
            print("No microphone found")
            exit()

    try:
        # Create and configure Voice Activity Detection
        vad = webrtcvad.Vad(3)
    except Exception as e:
        print(f"Could not initialize VAD: {e}")
        exit()

    # open mic
    try:
        stream = mic.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
    except IOError as e:
        print(f"Could not open stream: {e}")
        exit()

    try:
        process_audio(stream=stream, vad=vad, audio_queue=audio_queue)
    except KeyboardInterrupt:
        print("Exit Signal Recieved")
        stream.close()
        mic.terminate()
        exit()


def process_audio(stream: "pyaudio.Stream", vad: Vad, audio_queue: Queue):
    global NO_SPEECH_COUNT  # only needed as we are updating the variable
    # Debug counter for number of voice detections
    count = 0

    # initialize the DoA Angles
    theta = 0
    phi = 0

    # for smoothing the VAD results
    vad_results = deque(maxlen=10)

    # initialize the buffer
    print("* recording")
    BUFFER = []
    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
        except OSError as e:
            print(f"Could not read from stream: {e}")
            exit()
        # This comes in as a 1D array of 16bytes.
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Reshape audio to an array of [CHANNEL][CHUNK]. This way each chunk is it's own channel.
        reshaped_audio_data = np.reshape(
            audio_data, (CHUNK, CHANNELS)
        ).T  # shape will be (8, 2048)
        # print(reshaped_audio_data.shape)  # Should print (8, 2048)
        assert reshaped_audio_data.shape[0] == CHANNELS
        assert reshaped_audio_data.shape[1] == CHUNK

        is_speech_flag = is_speech(audio_data=audio_data, vad=vad)
        vad_results.append(is_speech_flag)

        # Smoothing Algorithm
        avg_vad = sum(vad_results) / len(vad_results)

        # Check if it contains speech
        if avg_vad > 0.5:
            print("Speech Detected ", count, " times")
            count += 1
            # reset No Speech counter
            NO_SPEECH_COUNT = 0
            # Perform beamforming

            # Direction of interest
            theta, phi = estimate_doa_with_music(
                reshaped_audio_data, mic_positions, RATE
            )

            # Calculate delays
            delays = calculate_delays(mic_positions, theta, phi)
            beamformed_audio = delay_and_sum(
                [audio_data], delays
            )  # You'd have multi-channel data in a real scenario
            BUFFER.extend(beamformed_audio)
        else:
            NO_SPEECH_COUNT += 1
            if NO_SPEECH_COUNT >= NO_SPEECH_LIMIT:
                print("No speech detected for 2 seconds")
                if len(BUFFER) > 0:
                    if count >= MIN_SPEECH_COUNT:
                        audio_chunk = np.array(BUFFER, dtype=np.int16).tobytes()
                        duration = len(BUFFER) / RATE  # Time in seconds
                        # Add data to queue
                        audio_queue.put(
                            {
                                "AudioData": audio_chunk,
                                "Duration": duration,
                                "theta": theta,
                                "phi": phi,
                                "channels": CHANNELS,
                                "sample_width": mic.get_sample_size(FORMAT),
                                "rate": RATE,
                            }
                        )
                    else:
                        print("Speech too short")
                    BUFFER.clear()
                    count = 0
                    if RECORD:
                        record(data, mic.get_sample_size(FORMAT))
                NO_SPEECH_COUNT = 0


def record(frames, sample_width):
    outputFile = wave.open("output.wav", "wb")
    outputFile.setnchannels(CHANNELS)
    outputFile.setsampwidth(sample_width)
    outputFile.setframerate(RATE)
    outputFile.writeframes(b"".join(frames))
    outputFile.close()


def is_speech(audio_data, vad: Vad):
    mono_audio_data = np.mean(np.reshape(audio_data, (CHANNELS, -1)), axis=0)
    return vad.is_speech(
        buf=mono_audio_data.astype(np.int16).tobytes(), sample_rate=RATE
    )
