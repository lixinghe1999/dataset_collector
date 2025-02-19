from utils.Audio.dataset import audio_sample
from utils.Audio.play import audio_prepare, chirp_play
import datetime


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Play audio')
    parser.add_argument('--left', type=str, default='TIMIT', help='left audio type')
    parser.add_argument('--right', type=str, default=None, help='right audio type')
    parser.add_argument('--db', type=float, default=-8, help='db')
    parser.add_argument('--sr', type=int, default=44100)
    parser.add_argument('--duration', type=float, default=5)
    args = parser.parse_args()
    left_audio_samples = audio_sample(args.left, 1)
    if args.right is None:
        right_audio_samples = left_audio_samples
    else:
        right_audio_samples = audio_sample(args.right, 1)
    for left_name, right_name in zip(left_audio_samples, right_audio_samples):
        stereo_audio = audio_prepare(left_name, right_name, int(args.duration * args.sr), args.sr, args.db)
        
        start_time = datetime.datetime.now()
        save_log = 'dataset/log/' + start_time.strftime('%Y%m%d_%H%M%S') + '.txt'
        chirp_play(stereo_audio, args.sr)
        # save the log: left_name, right_name
        with open(save_log, 'w') as f:
            f.write(left_name + '\n')
            f.write(right_name + '\n')