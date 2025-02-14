'''
Run this script to play random audio from the dataset with speakers
'''
import librosa
import sounddevice as sd
import numpy as np
from Audio.audio_dataset import audio_sample, get_chirp
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

    
def prepare(config):
    duration_samples = int(config['duration'] * config['sr'])

    left_audio_samples = audio_sample(config['left_type'], config['num'])
    if config['mono']:
        right_audio_samples = left_audio_samples
    else:
        right_audio_samples = audio_sample(config['right_type'], config['num'])
    audio_play_list = []; random_crops = []
    for left_audio, right_audio in zip(left_audio_samples, right_audio_samples):
        left_audio, fs = librosa.load(left_audio, sr=config['sr'])
        right_audio, fs = librosa.load(right_audio, sr=config['sr'])
        
        left_length = len(left_audio); right_length = len(right_audio)
        max_length = max(left_length, right_length)

        left_audio = np.pad(left_audio, (0, max_length - left_length))
        random_dbfs = np.random.uniform(-5, 5)
        left_audio = adjust_audio_dbfs(left_audio, config['db'] + random_dbfs)

        right_audio = np.pad(right_audio, (0, max_length - right_length))
        random_dbfs = np.random.uniform(-5, 5)
        right_audio = adjust_audio_dbfs(right_audio, config['db'] + random_dbfs)

        if duration_samples >= max_length:
            active_samples = [0, max_length]
        else:
            random_start = random.randint(0, max_length - duration_samples)
            active_samples = [random_start, random_start + duration_samples]

        stereo_audio = np.stack([left_audio, right_audio], axis=1)
        print(active_samples)
        stereo_audio = stereo_audio[active_samples[0]:active_samples[1]] # only crop the random part of it
        audio_play_list.append(stereo_audio)
        random_crops.append(active_samples)
        print('prepare one audio with length:', max_length)
    
    # add chirp to denote the start of the audio
    chirp = get_chirp(sample_rate=config['sr'], duration=1.0, min_freq=2000, max_freq=4000)
    stereo_chirp = np.stack([chirp, chirp], axis=1)
    # append the chirp to the audio

    start_time = datetime.datetime.now()
    save_log = 'dataset/log/' + start_time.strftime('%Y%m%d_%H%M%S') + '.txt'
    with open(save_log, 'w') as f:
        f.write('left_audio right_audio start end\n')
        # save the audio name
        for left_audio, right_audio, crop in zip(left_audio_samples, right_audio_samples, random_crops):
            crop_start_sec = crop[0] / config['sr']
            crop_end_sec = crop[1] / config['sr']
            f.write(left_audio + ' ' + right_audio + ' ' + str(crop_start_sec) + ' ' + str(crop_end_sec) + '\n')
    audio = np.concatenate ([stereo_chirp] + audio_play_list, axis=0)
    print('Playing audio...')
    sd.play(audio, fs, blocking=True)
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Play audio')
    parser.add_argument('--left', type=str, default='NIGENS', help='left audio type')
    parser.add_argument('--right', type=str, default=None, help='right audio type')
    parser.add_argument('--mono', default=True, action='store_true', help='mono audio')
    parser.add_argument('--db', type=float, default=-8, help='db')
    parser.add_argument('--num', type=int, default=5)
    parser.add_argument('--sr', type=int, default=44100)
    parser.add_argument('--duration', type=float, default=5)
    args = parser.parse_args()

    config = {'left_type': args.left, 'right_type': args.right, 'mono': args.mono, 'db': args.db, 'sr': args.sr, 'num': args.num, 'duration': args.duration}
    audio = prepare(config)
