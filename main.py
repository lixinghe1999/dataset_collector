import argparse
import datetime
import os
import multiprocessing
from utils.Audio.record import receive_audio
from utils.IMU.bmi160 import receive_imu


def audio_recording(dataset_folder, device, duration):
    if duration > 0:
        receive_audio(dataset_folder, device=device, duration=duration)
    else:  # duration = -1, infinite loop for data recording
        while True:
            segment_duration = 10
            receive_audio(dataset_folder, device=device, duration=segment_duration)
def imu_recording(dataset_folder, sample_rate, duration, port):
    if duration > 0:
        receive_imu(dataset_folder, sample_rate=sample_rate, t=duration, port=port)
    else:  # duration = -1, infinite loop for data recording
        while True:
            segment_duration = 10
            receive_imu(dataset_folder, sample_rate=sample_rate, t=segment_duration, port=port)


def main():
    parser = argparse.ArgumentParser()

    # General mode selection
    parser.add_argument('--mode', type=str, choices=['audio', 'imu', 'both'], required=True,
                        help="Select mode: 'audio' for audio-only, 'imu' for IMU-only, 'both' for both.")

    # Audio recording arguments
    parser.add_argument('--device', type=str, nargs='+', default=["Yundea"], help="Audio device(s) to use (e.g., Yundea, Device)")    
    parser.add_argument('--duration', type=int, default=1, help="Duration of audio recording in seconds (-1 for infinite)")
    parser.add_argument('--sample_rate', type=int, default=48000, help="Audio sample rate")
    # parser.add_argument('--channels', type=int, default=2, help="Number of audio channels")
    
    # IMU data collection arguments
    parser.add_argument('--imu_sample_rate', type=int, default=100, help="IMU sample rate")
    parser.add_argument('--imu_port', type=int, default=1, help="Port for IMU data collection")

    args = parser.parse_args()

    # Create the dataset folder
    os.makedirs('recording', exist_ok=True)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    dataset_folder = os.path.join('recording', date_str)
    os.makedirs(dataset_folder, exist_ok=True)

    # Create processes for audio and IMU data collection
    processes = []

    if args.mode in ['audio', 'both']:
        audio_process = multiprocessing.Process(target=audio_recording, args=(dataset_folder, args.device, args.duration))
        processes.append(audio_process)

    if args.mode in ['imu', 'both']:
        imu_process = multiprocessing.Process(target=imu_recording, args=(dataset_folder, args.imu_sample_rate, args.duration, args.imu_port))
        processes.append(imu_process)

    # Start all processes
    for process in processes:
        process.start()

    # Join all processes to wait for them to finish
    for process in processes:
        process.join()

if __name__ == '__main__':
    main()