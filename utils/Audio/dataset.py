'''
select a random audio sample from the ESC50 and TIMIT by type
'''
import pandas as pd
import random
import os
import soundfile as sf
import librosa

def get_chirp(sample_rate=44100, duration=5.0, min_freq=100, max_freq=8000, save_name=None):
    import numpy as np
    from scipy.io import wavfile
    t = np.linspace(0, duration, int(duration * sample_rate), False)
    chirp = np.sin(2 * np.pi * (min_freq + (max_freq - min_freq) * t / duration) * t)
    # Save the chirp to a WAV file
    if save_name is not None:
        sf.write(save_name, chirp, sample_rate)
    return chirp

def TIMIT_sample(num_samples=1):
    folder = 'dataset/TIMIT/TRAIN/'
    filtered_audio_list = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".WAV"):
                filtered_audio_list.append(os.path.join(root, file))
    random_audio = random.sample(filtered_audio_list, num_samples)
    return random_audio



def ESC50_sample(category, num_samples=1):
    esc50_subtask = {
    'natural': ['rain', 'sea_waves', 'crickets', 'chirping_birds', 'water_drops', 'wind', 'pouring_water', 'toilet_flush', 'thunderstorm'],
    'human': ['crying_baby', 'sneezing', 'clapping', 'breathing', 'coughing', 'footsteps', 'laughing', 'brushing_teeth', 'snoring', 'drinking_sipping'],
    'domestic': ['door_wood_knock', 'mouse_click', 'keyboard_typing', 'door_wood_creaks', 'can_opening', 'washing_machine', 'vacuum_cleaner', 'clock_alarm', 'clock_tick', 'glass_breaking'],
    'urban':['helicopter', 'chainsaw', 'siren', 'car_horn', 'engine', 'train', 'church_bells', 'airplane', 'fireworks', 'hand_saw'],
    } 
    assert category in ['natural', 'human', 'domestic', 'urban']
    folder = 'dataset/ESC-50-master/audio/'
    meta_esc50 = pd.read_csv(folder + '../meta/esc50.csv')
    category = random.choice(esc50_subtask[category])
    filtered_audio_list = meta_esc50[meta_esc50.category == category].filename.tolist()
    filtered_audio_list = [folder + audio for audio in filtered_audio_list]
    random_audio = random.sample(filtered_audio_list, num_samples)
    return random_audio

def NIGENS_sample(num_samples=1):
    folder = 'dataset/NIGENS/'
    filtered_audio_list = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".wav"):
                filtered_audio_list.append(os.path.join(root, file))
    random_audio = random.sample(filtered_audio_list, num_samples)
    return random_audio

def audio_sample(category, num_samples=1):
    if category == 'TIMIT':
        return TIMIT_sample(num_samples)
    elif category == 'NIGENS':
        return NIGENS_sample(num_samples)
    elif category in ['natural', 'human', 'domestic', 'urban']:
        return ESC50_sample(category, num_samples)
    else:
        raise ValueError('Invalid category')
# if __name__ == '__main__':
#     # audio = NIGENS_sample()

#     sine_wave = get_chirp(sample_rate=44100, duration=1.0, min_freq=2000, max_freq=4000)

#     import matplotlib.pyplot as plt
#     import numpy as np

#     self_correlation = np.correlate(sine_wave, sine_wave, mode='full')
#     plt.plot(self_correlation)
#     plt.show()

