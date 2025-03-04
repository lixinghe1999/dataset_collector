from utils.Audio.record import receive_audio
import datetime
import os 
import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=str, default="Yundea") # Yundea - 8Mics, Device - 2Mics,Binaural
    parser.add_argument('--duration', type=int, default=1)
    parser.add_argument('--sample_rate', type=int, default=48000)
    parser.add_argument('--channels', type=int, default=2)
    args = parser.parse_args()

    os.makedirs('recording', exist_ok=True)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    dataset_folder = os.path.join('recording', date_str)
    os.makedirs(dataset_folder, exist_ok=True)
    
    CHUNK_RECORD = 10
    num_chunks = args.duration // CHUNK_RECORD
    for i in range(num_chunks+1):
        receive_audio(dataset_folder, device=args.device, fs=args.sample_rate, duration=CHUNK_RECORD, channels=args.channels)