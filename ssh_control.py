import paramiko


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
if __name__ == '__main__':
    import argparse
    import datetime
    parser = argparse.ArgumentParser()
    parser.add_argument("--imu", type=int, default=2) # 0: no imu, 1: left, 2: right, 3: both
    parser.add_argument("--camera", type=int, default=1) # 0: no camera, 1: yes
    parser.add_argument("--audio", type=int, default=1) # 0: no audio, 1: Binaural
    parser.add_argument("--time", type=str, default=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    parser.add_argument("-d", "--duration", type=int, default=5)
    args = parser.parse_args()

    client = create_connection()
    print("Connected to the server")

    # execute_command(client, 'ls -l')
    # command = 'nohup python main.py --imu 3 --audio 1 --time 2021-09-01_12-00-00 &'
    command = '~/miniforge3/envs/hmw/bin/python main.py --imu {} --camera {} --audio {} --time {} --duration {}'\
                    .format(args.imu, args.camera, args.audio, args.time, args.duration)

    stdin, stdout, stderr = client.exec_command('cd ~/localization/dataset; ' + command)

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
