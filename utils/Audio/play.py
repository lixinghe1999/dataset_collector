'''
Run this script to play random audio from the dataset with speakers
'''
import librosa
import sounddevice as sd
import numpy as np
from utils.Audio.dataset import get_chirp
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
    left_audio, fs = librosa.load(left_name, sr=sr)
    right_audio, fs = librosa.load(right_name, sr=sr)
    
    random_dbfs = np.random.uniform(-5, 5)
    left_audio = adjust_audio_dbfs(left_audio, db + random_dbfs)

    random_dbfs = np.random.uniform(-5, 5)
    right_audio = adjust_audio_dbfs(right_audio, db + random_dbfs)
    
    max_length = max(len(left_audio), len(right_audio))
    stereo_audio = np.zeros((max_length, 2))
    stereo_audio[:len(left_audio), 0] = left_audio
    stereo_audio[:len(right_audio), 1] = right_audio
    if duration_samples < max_length:
        stereo_audio = stereo_audio[:duration_samples]
    
    return stereo_audio

def chirp_play(stereo_audio, sr):   
    # add chirp to denote the start of the audio
    chirp = get_chirp(sample_rate=sr, duration=1.0, min_freq=2000, max_freq=4000)
    stereo_chirp = np.stack([chirp, chirp], axis=1)
    # stereo_audio = np.concatenate([stereo_chirp, stereo_audio], axis=0)
    print('Playing audio...')
    sd.play(stereo_audio, sr, blocking=True)
    

