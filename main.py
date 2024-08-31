import datetime
import os
import argparse
import multiprocessing as mp
def create_connection():
    # SSH connection details
    hostname = "192.168.137.172"
    username = "pi"
    password = "123456"

    # Create an SSH client
    client = paramiko.SSHClient()

    # Automatically add the host key (not recommended for production)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SSH server
    client.connect(hostname=hostname, username=username, password=password)
    
    return client

def remote_main(client, args):
    command = '~/miniforge3/envs/hmw/bin/python main.py --imu {} --camera {} --audio {} --time {} --duration {}'\
                    .format(args.imu, args.camera, args.audio, args.time, args.duration)
    stdin, stdout, stderr = client.exec_command('cd ~/dataset_collector/; ' + command)
    # Wait for the command to complete
    exit_status = stdout.channel.recv_exit_status()
    # Check the exit status
    if exit_status == 0:
        print("Command executed successfully")
        print(stdout.read().decode())
    else:
        print("Command failed with exit status:", exit_status)
        error = stderr.read().decode()
        print("Command error:", error)
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--imu", type=int, default=0) # 0: no imu, 1: left, 2: right, 3: both
    parser.add_argument("--camera", type=int, default=0) # 0: no camera, 1: yes
    parser.add_argument("--audio", type=int, default=0) # 0: no audio, 1: Binaural
    parser.add_argument("--time", type=str, default=None)
    parser.add_argument("-d", "--duration", type=int, default=5)
    parser.add_argument("--remote", action='store_true')
    args = parser.parse_args()
    
    if args.time == None:
        args.time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    pre_date = args.time.split('_')[0]
    post_date = args.time.split('_')[1]
    if args.remote:
        import paramiko
        # collect data remotely
        client = create_connection()
        remote_main(client, args)
    else:
        import sys
        sys.path.append('./IMU')
        from IMU.bmi160 import bmi160
        from Audio.mic import receive_audio
        dataset_folder = os.path.join('dataset', pre_date, post_date)
        os.makedirs(dataset_folder, exist_ok=True)
        process_list = []
        if args.imu != 0:
            if args.imu == 1 or args.imu == 3:
                p1 = mp.Process(target=bmi160, args=(dataset_folder, 200, args.duration, 0))
                process_list.append(p1)
            if args.imu == 2 or args.imu == 3:
                p2 = mp.Process(target=bmi160, args=(dataset_folder, 200, args.duration, 1))
                process_list.append(p2)
        if args.audio == 1:
            p4 = mp.Process(target=receive_audio, args=(dataset_folder, 48000, args.duration, 2))
            process_list.append(p4)
        else:
            p5 = mp.Process(target=receive_audio, args=(dataset_folder, 48000, args.duration, 8))
            process_list.append(p5)
        

        for p in process_list:
            p.start()
        for p in process_list:
            p.join()    
        