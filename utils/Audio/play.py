'''
Run this script to play random audio from the dataset with speakers
'''
import librosa
import sounddevice as sd
import numpy as np
# from utils.Audio.dataset import get_chirp
import datetime
import random

def adjust_audio_dbfs(audio, target_dbfs):
    # Load the audio file
    # Function to convert dB to linear scale
    def db_to_linear(db):
        return 10 ** (db / 20)

    # Calculate the current dBFS of the audio
    current_dbfs = 20 * np.log10(np.max(np.abs(audio)))

    # Calculate the change needed
    change_in_db = target_dbfs - current_dbfs

    # Adjust the audio signal
    audio_adjusted = audio * db_to_linear(change_in_db)

    # Ensure the audio remains in the valid range
    audio_adjusted = np.clip(audio_adjusted, -1, 1)
    return audio_adjusted

def audio_prepare(left_name, right_name, duration_samples, sr, db):
    random_dbfs = np.random.uniform(-5, 5)
    if left_name is None:
        left_audio = np.zeros(duration_samples)
    else:
        left_audio, fs = librosa.load(left_name, sr=sr)
        left_audio = adjust_audio_dbfs(left_audio, db + random_dbfs)

    if right_name is None:
        right_audio = np.zeros(duration_samples)
    else:
        right_audio, fs = librosa.load(right_name, sr=sr)
        right_audio = adjust_audio_dbfs(right_audio, db + random_dbfs)
    max_length = max(len(left_audio), len(right_audio))
    stereo_audio = np.zeros((max_length, 2))
    stereo_audio[:len(left_audio), 0] = left_audio
    stereo_audio[:len(right_audio), 1] = right_audio
    if duration_samples < max_length:
        stereo_audio = stereo_audio[:duration_samples]
    
    return stereo_audio

def chirp_play(stereo_audio, sr, chirp=True):   
    if chirp:
        # add chirp to denote the start of the audio
        chirp = get_chirp(sample_rate=sr, duration=1.0, min_freq=2000, max_freq=4000)
        stereo_chirp = np.stack([chirp, chirp], axis=1)
        stereo_audio = np.concatenate([stereo_chirp, stereo_audio], axis=0)
    print('Playing audio...')
    sd.play(stereo_audio, sr, blocking=True)
    
def play_audio(play_file, device, duration=5):
    '''
    Play audio from a specified file with a given device.
    '''
    audio, sr = librosa.load(play_file, sr=None)
    if len(audio) < duration * sr:
        # repeat the audio to fill the duration
        audio = np.tile(audio, int(np.ceil((duration * sr) / len(audio))))
    audio = audio[:duration * sr]  # trim to the exact duration
    sd.play(audio, samplerate=sr, device=device,)
    sd.wait()  # Wait until the audio is finished playing
    print(f'Audio played from {play_file} on device {device} for {duration} seconds.')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Record audio from a specified device.')
    parser.add_argument('--play_file', type=str, required=True)
    parser.add_argument('--device', type=int, required=True,)
    parser.add_argument('--duration', type=int, default=5, help='Duration of the audio to play in seconds')

    args = parser.parse_args()
    play_audio(args.play_file, args.device, args.duration)

