from utils.Audio.audio_record import receive_audio
import datetime
import os 
import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--duration', type=int, default=1)
    parser.add_argument('--sample_rate', type=int, default=48000)
    parser.add_argument('--channels', type=int, default=2)
    args = parser.parse_args()

    os.makedirs('recording', exist_ok=True)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    dataset_folder = os.path.join('recording', date_str)
    os.makedirs(dataset_folder, exist_ok=True)
    
    receive_audio(dataset_folder, fs=args.sample_rate, duration=args.duration, channels=args.channels)