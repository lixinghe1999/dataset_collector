'''
1. use the chirp the locate the audio
2. synchronize audio and IMU
'''
import os
import matplotlib.pyplot as plt
import librosa
from audio_sample import get_chirp
import numpy as np
import json 
dataset_path = 'log/2024-08-19/'
files = os.listdir(dataset_path)
files = [f for f in files if not f.endswith('.json')] # remove the annotation files
for file in files:
    data_folder = os.path.join(dataset_path, file)
    print(data_folder, file)
    annotation_file = os.path.join(dataset_path, file + '.json')
    annotation = json.load(open(annotation_file, 'r'))
    left_audio = annotation['left_audio']

    right_audio = annotation['right_audio']
    if right_audio == None:
        right_audio = left_audio
    left_audio = librosa.load(left_audio, sr=None)[0]
    right_audio = librosa.load(right_audio, sr=None)[0]
    real_length = len(left_audio)

    datas = os.listdir(data_folder)
    audio_file = [f for f in datas if f.endswith('.wav')][0]
    imu_file = ['bmi160_0.txt', 'bmi160_1.txt']
    # camera_file = ['depth.avi', 'ir.avi']

    audio, fs = librosa.load(os.path.join(data_folder, audio_file), sr=None)
    chirp = get_chirp(sample_rate=fs, duration=0.5, min_freq=100, max_freq=2000)

    correlation = np.correlate(audio, chirp, mode='full')[:fs]
    correlation = np.abs(correlation)
    offset = np.argmax(correlation) + len(chirp)
    audio_crop = audio[offset:offset+real_length]
    left_corr = np.correlate(audio_crop, left_audio, mode='valid')
    right_corr = np.correlate(audio_crop, right_audio, mode='valid')
    print(left_corr, right_corr)

    fig, ax = plt.subplots(5, 1, figsize=(10, 5))
    ax[0].plot(audio)
    ax[0].set_title('Audio')
    ax[1].plot(correlation)
    ax[1].set_title('Correlation')
    ax[2].plot(audio_crop)
    ax[2].set_title('Audio Crop')
    plt.show()