import sounddevice as sd
import wave
import os
import datetime


def get_device_index_by_name(device_name):
    devices = sd.query_devices()
    devices = [(i, device['name']) for i, device in enumerate(devices)]
    matching_devices = [(index, name) for index, name in devices if device_name.lower() in name.lower()]

    if matching_devices:
        # Sort by index priority (lower index preferred)
        matching_devices.sort(key=lambda x: x[0])
        return matching_devices[0][0], matching_devices[0][1] # Return the index of the first match
    return 0, 'default'
def receive_audio(dataset_folder, device, fs=48000, duration=5, channels=2):
    '''
    receive by sounddevice and save the audio data
    '''
    idx, device_name = get_device_index_by_name(device)
    print(f'Using device index: {idx}, device name: {device_name}')
    # Set the parameters
    sd.default.device = idx
    default_channels = sd.query_devices(sd.default.device[1])['max_input_channels']
    default_sample_rate = sd.query_devices(sd.default.device[1])['default_samplerate']
    if default_sample_rate != fs:
        fs = default_sample_rate
        channels = default_channels

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
    receive_audio('.')