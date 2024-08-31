'''
select a random audio sample from the ESC50 and TIMIT by type
'''
import pandas as pd
import random
import os
import scipy.io.wavfile as wavfile
import librosa
def get_chirp(sample_rate=44100, duration=5.0, min_freq=100, max_freq=8000, save_name=None):
    import numpy as np
    from scipy.io import wavfile
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    chirp = np.sin(2 * np.pi * (min_freq + (max_freq - min_freq) * t / duration) * t)
    # Save the chirp to a WAV file
    if save_name is not None:
        wavfile.write(save_name, sample_rate, (chirp * 32767).astype(np.int16))
    return chirp

def audio_sample(category):
    if category == 'speech':
        folder = 'TIMIT/TRAIN/'
        filtered_audio_list = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".WAV"):
                    filtered_audio_list.append(os.path.join(root, file))
    else:
        folder = 'ESC-50-master/audio/'
        meta_esc50 = pd.read_csv(folder + '../meta/esc50.csv')
        filtered_audio_list = meta_esc50[meta_esc50.category == category].filename.tolist()
        filtered_audio_list = [folder + audio for audio in filtered_audio_list]

    random_audio = random.choice(filtered_audio_list)
    return random_audio

def selected_audio_sample(name):
    return f'selected_dataset/{name}.wav'

def sparse_to_fill(audio_name):
    import matplotlib.pyplot as plt
    audio, fs = librosa.load(audio_name, sr=16000)
    audio_segments = librosa.effects.split(audio, top_db=20)

    fig, ax = plt.subplots()
    ax.plot(audio)
    ax.set_title('Audio waveform')
    for i, segment in enumerate(audio_segments):
        ax.axvline(segment[0], color='r')
        ax.axvline(segment[1], color='r')
    plt.show()
    print('Audio segments:', audio_segments)
    return audio

if __name__ == '__main__':
    for max_freq in [2000, 4000, 8000, 16000]:
        get_chirp(save_name=f'selected_dataset/chirp_{max_freq}.wav', max_freq=max_freq)
    for single_freq in [400, 800, 1600]:
        get_chirp(save_name=f'selected_dataset/sin_{single_freq}.wav', min_freq=single_freq, max_freq=single_freq)
    # audio_name = audio_sample('dog')
    # audio = sparse_to_fill(audio_name)
