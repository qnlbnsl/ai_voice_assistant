from multiprocessing import Queue

from audio_stream.socket import init_connection, send_to_server, close_connection


def initialize_server_communication(audio_queue: Queue):
    init_connection()
    try:
        while True:
            # Check if there is something in the queue
            if not audio_queue.empty():
                data = audio_queue.get()

                audio_data = data["AudioData"]
                duration = data["Duration"]
                theta = data["theta"]
                phi = data["phi"]

                # Now do something with the data, such as send it to the server
                send_to_server(audio_data, duration, theta, phi)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting.")
        close_connection()
        exit(0)
