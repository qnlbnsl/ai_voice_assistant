import wave
import time
import numpy as np

from logger import logger


def record(audio_bytes: bytes, channels, sample_width, rate):
    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    outputfile_name = f"outfile-{timestamp}.wav"
    logger.info(len(audio_bytes))
    with wave.open(outputfile_name, "wb") as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(rate)
        wav_file.writeframes(audio_bytes)
        logger.info(f"Audio saved to {outputfile_name}")
