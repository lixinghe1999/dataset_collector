import sounddevice as sd
import wave
import os
import datetime

def get_device_index_by_list(device_names):
    for device_name in device_names:
        idx, device_name = get_device_index_by_name(device_name)
        if device_name != 'default':
            return idx, device_name
    return 0, 'default'

def get_device_index_by_name(device_name, record=True): 
    print(f'Looking for device: {device_name}')
    devices = sd.query_devices()
    if record: # only keep the microphone, input devices
        devices = [device for device in devices if device['max_input_channels'] > 0]
    else: # only keep the speaker, output devices
        devices = [device for device in devices if device['max_output_channels'] > 0]
    
    devices = [(device['index'], device['name']) for i, device in enumerate(devices)]
    matching_devices = [(index, name) for index, name in devices if device_name.lower() in name.lower()]

    if matching_devices:
        # Sort by index priority (lower index preferred)
        matching_devices.sort(key=lambda x: x[0])
        return matching_devices[0][0], matching_devices[0][1] # Return the index of the first match
    return devices[0]


def receive_audio(dataset_folder, device, duration=5):
    '''
    receive by sounddevice and save the audio data
    '''
    # if type(device) == str:
    #     idx, device_name = get_device_index_by_name(device)
    # else:
    if isinstance(device, list):
        idx, device_name = get_device_index_by_list(device)
    else:
        idx = device
        device_name = sd.query_devices(idx)['name']
    # Set the parameters
    sd.default.device = idx
    fs = sd.query_devices(sd.default.device[1])['default_samplerate']
    channels = sd.query_devices(sd.default.device[1])['max_input_channels']
    print(f'Using device index: {idx}, device name: {device_name}, fs: {fs}, channels: {channels}')
    # default_channels = sd.query_devices(sd.default.device[1])['max_input_channels']
    # default_sample_rate = sd.query_devices(sd.default.device[1])['default_samplerate']
    # if default_sample_rate != fs:
    #     fs = default_sample_rate
    #     channels = default_channels

    datetime_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
    filename = os.path.join(dataset_folder, f'{datetime_str}.wav')
    # Record the audio
    print('Recording audio start...')
    myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=channels, dtype='int16')
    sd.wait()
    print('Recording audio done ...')
    waveFile = wave.open(filename, 'wb')
    waveFile.setnchannels(channels) 
    waveFile.setsampwidth(2)
    waveFile.setframerate(fs)
    waveFile.writeframes(myrecording)
    waveFile.close()
    print(f'Audio saved at {filename} ...')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Record audio from a specified device.')
    parser.add_argument('--dataset_folder', type=str, required=True)
    parser.add_argument('--device', type=int, required=True,)
    parser.add_argument('--duration', type=int, default=5, help='Duration of the recording in seconds.')

    args = parser.parse_args()
    receive_audio(args.dataset_folder, args.device, args.duration)