from Vision.usb_cam_record import video_record
import multiprocessing as mp
import json
import datetime
import subprocess
import os
if __name__ == '__main__':
    while True:
        a = input('press 1 to play audio (edit the config first), press 2 to exit: ')
        if a == '1':
            config_file = 'config.json'
            log = json.load(open(config_file, 'r'))
            current_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            log['time'] = current_time
            p_remote = mp.Process(target=subprocess.run, args=('python main.py --imu 3 --audio 1 --time {} --remote'.format(current_time),))
            p_local = mp.Process(target=video_record, args=('dataset', 5, False))
            p_remote.start()
            p_local.start()
            p_remote.join()
            p_local.join()

            pre, post = current_time.split('_')
            if not os.path.exists('dataset/' + pre):
                os.makedirs('dataset/' + pre)   
            with open(f'dataset/{pre}/{post}.json', 'w') as f:
                json.dump(log, f, indent=4)
        elif a == '2':
            exit()

p_local = mp.Process(target=video_record, args=('dataset', 5))
p_remote = mp.Process()
