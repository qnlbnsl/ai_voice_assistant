import time
import numpy as np
from numpy.typing import NDArray
from multiprocessing.synchronize import Event
from multiprocessing import Queue
from faster_whisper.transcribe import Segment

from speech_to_text.buffers.circular_buffer import CircularBuffer
from speech_to_text.transcribe import WhisperModelManager
from logger import logger

# Initialize the circular buffer
MAX_BUFFER_DURATION = 4  # seconds # 100 samples  at 40ms per sample


def stt(
    shutdown_event: Event,
    decoded_audio_queue: "Queue[NDArray[np.float32]]",
    transcribed_text_queue: "Queue[str]",
    concept_queue: "Queue[Segment]",
    stt_ready_event: Event,
    wake_word_event: Event,
) -> None:
    model_manager = WhisperModelManager()
    logger.info("STT Ready")
    try:
        circular_buffer = CircularBuffer(
            capacity=MAX_BUFFER_DURATION, sample_rate=16000
        )
        duration = 0.0
        # this function is only going to start when model is loaded.
        # that happens when all imports are being evaluated.
        stt_ready_event.set()  # Signal that STT is ready
        logger.debug("Waiting for data to be added to buffer")
        while shutdown_event.is_set() is False:
            try:
                new_data = decoded_audio_queue.get()
                circular_buffer.write(new_data)
                # logger.debug("Data added to buffer")
            except Exception as e:
                logger.debug(f"Error in getting data from Queue: {e}")
                pass

            # If buffer is full , transcribe it
            buffer_duration = circular_buffer.get_buffer_duration()
            time_since_last_write = time.time() - circular_buffer.last_write_time
            if duration == buffer_duration:
                continue
            else:
                duration = buffer_duration
                # logger.debug("Buffer duration: " + str(buffer_duration))

            # Begin transcription if buffer is half full or if it has been 2 seconds since last transcription
            if buffer_duration >= (MAX_BUFFER_DURATION / 2) or (
                time_since_last_write > 2 and buffer_duration > 0.5
            ):
                # logger.debug("Transcription condition met. Starting transcription")
                audio_chunk = circular_buffer.read(buffer_duration)
                if audio_chunk:
                    model_manager.transcribe_chunk(
                        audio_chunk,
                        transcribed_text_queue,
                        concept_queue,
                        wake_word_event,
                    )
            # time.sleep(0.1)  # Sleep for 100ms
        logger.debug("Transcription thread exiting")
    except Exception as e:
        logger.error(f"Error in transcribe: {e}")
        raise e
