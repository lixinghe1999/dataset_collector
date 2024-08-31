'''
Run this script to play random audio from the dataset with speakers
'''
import os
import librosa
import sounddevice as sd
import numpy as np
import datetime
from Audio.audio_sample import audio_sample, get_chirp, selected_audio_sample
import time

def prepare(log):
    # Importing the necessary libraries
    log['left_audio'] = selected_audio_sample(log['left_type'])
    if log['mono']:
        log['right_audio'] = None
    else:
        log['right_audio'] = selected_audio_sample(log['right_type'])
    print(f'Playing audio: {log["left_audio"]} and {log["right_audio"]}')
    audios = []
    for audio_file in [log['left_audio'], log['right_audio']]:
        if audio_file is None:
            audios.append(np.zeros((16000, 1)))
        else:
            audio, fs = librosa.load(audio_file, sr=16000)
            audios.append(audio[:, None])   
    n_sample = 0
    for audio in audios:
        n_sample = max(audio.shape[0], n_sample)

    # chirp = get_chirp(sample_rate=fs, duration=0.5, min_freq=8000, max_freq=12000)
    for i, audio in enumerate(audios):
        if audio.shape[0] < n_sample:
            audios[i] = np.pad(audio, ((0, n_sample - audio.shape[0]), (0, 0)), 'constant')  
        # audios[i] = np.concatenate([chirp[:, None], audios[i]], axis=0)

    audio = np.concatenate(audios, axis=1)
    print('Playing audio... with shape:', audio.shape)
    return log, audio, fs
def play(audio, fs):
    time.sleep(1) # wait the recording start
    sd.play(audio, fs, blocking=True)
    print('Finished playing audio')
    
if __name__ == '__main__':
    import json
    import multiprocessing
    import subprocess

    while True:
        a = input('press 1 to play audio (edit the config first), press 2 to exit: ')
        if a == '1':
            config_file = 'collect_config.json'
            log = json.load(open(config_file, 'r'))
            current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            log['time'] = current_time
            log, audio, fs = prepare(log)
            # subprocess.run('python ssh_control.py --time {}'.format(current_time), shell=True)
            # use multiprocessing to run the command on client and run main function
            p1 = multiprocessing.Process(target=subprocess.run, args=('python main.py --time {} --remote'.format(current_time),))
            p2 = multiprocessing.Process(target=play, args=(audio, fs))
            p1.start()
            p2.start()
            p1.join()
            p2.join()

            pre, post = current_time.split('_')
            if not os.path.exists('log/' + pre):
                os.makedirs('log/' + pre)   
            with open(f'log/{pre}/{post}.json', 'w') as f:
                json.dump(log, f, indent=4)
        elif a == '2':
            exit()
        
        