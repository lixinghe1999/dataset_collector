
import os
import datetime
import FreeSimpleGUI as sg
import os
import sys
import subprocess
import time
import threading
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.Audio.record import get_device_index_by_name

full_transcript = "loggers/aishell_transcript_v0.8.txt"

def init_layout_speech():
    '''
    Initialize the layout for the GUI.
    '''
    font_size = 14
    sensor_type = ['KN BPs USB',]
    # convert to a selectable list in gui (multiple choices)
    sensor_type = [sg.Listbox(sensor_type, size=(80, 4), key='sensor', default_values=[], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE )]

    speaker_type = ['AirPods Pro #2 Stereo', 'none']
    speaker_type = [sg.Listbox(speaker_type, size=(40, 4), key='speaker', default_values=['none'], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE),
                    sg.Listbox(['OFDM', 'FMCW', 'test', 'none'], size=(40, 4), key='proble_signal', default_values=['test'], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)]

    layout = [
        [sg.Text('Recording devices (multi-choices)', font=('Helvetica', font_size), justification='center')],
        sensor_type,
        [sg.Text('Playback devices (single-choice), if Yes, at least one probe signal is required', font=('Helvetica', font_size), justification='center')],
        speaker_type,
        [sg.Text("Volunteer Name:",  font=('Helvetica', font_size), size=(font_size, 1)), sg.InputText(size=(font_size, 1), key='volunteer', default_text='LixingHe')],
        [sg.Button('Confirm', font=('Helvetica', font_size), size=(15, 1)), sg.Text('Not confirmed', size=(20, 1), key='confirm', font=('Helvetica', font_size), text_color='red')],
        
        [sg.Text("Recording time:", font=('Helvetica', font_size), size=(15, 1)),     
            sg.InputText(size=(15, 1), font=('Helvetica', font_size), key='recording_time', default_text='10'),
            sg.Text("", size=(30, 1), font=('Helvetica', font_size), text_color='red', key='remaining_time')],

        [sg.Text('Please read the below content: ', font=('Helvetica', font_size), size=(60, 2), key='content')],
        [sg.Button('Start Recording', font=('Helvetica', font_size), size=(font_size, 1))],

        # [sg.Button('Stop Recording', font=('Helvetica', font_size), size=(font_size, 1))],
        [sg.Button('Redo', font=('Helvetica', font_size), size=(font_size, 1))],
        [sg.Button('Exit',  font=('Helvetica', font_size), size=(font_size, 1))]
    ]
    return layout

def device_parser(device_type, record=True):
    print('Selected device type:', device_type)
    if len(device_type) == 0:
        print('No device selected, please select at least one device.')
        return None
    for device in device_type:
        device_index, device_name = get_device_index_by_name(device, record=record)
        print(f'Using device index: {device_index}, device name: {device_name}')
    return device_index\
    
global isRecording
isRecording = False

def countdown_timer(seconds, window):
    global isRecording
    for remaining in range(seconds, 0, -1):
        window['remaining_time'].update(f'Time Remaining: {remaining} seconds')
        time.sleep(1)
    window['remaining_time'].update('')  # Reset after countdown
    isRecording = False

def record_speech(window):
    global isRecording
    transcripts = open(full_transcript, 'r', encoding='utf-8').readlines()
    len_transcripts = len(transcripts)
    parent_dicteroy = 'recording'
    confirm = False
    transcript_count = 0
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit': # if user closes window or clicks cancel
             break
        if event == 'Confirm':
            sensor_type = window['sensor'].get(); speaker_type = window['speaker'].get()
            if len(sensor_type) == 0 or len(speaker_type) == 0:
                sg.popup_error('Please select at least one recording device and one playback device.')
                window['confirm'].update('not confirmed', text_color='red')
                continue
            elif speaker_type[0] != 'none' and window['proble_signal'].get()[0] == 'none':
                sg.popup_error('Please select a playback device or a problem signal.')
                window['confirm'].update('not confirmed', text_color='red')
                continue
            # obtain the recording and playback functions
            record_index = device_parser(sensor_type, record=True)
            play_index = device_parser(speaker_type, record=False)
            
            volunteer_name = window['volunteer'].get()
            folder_name = f"{volunteer_name}_{datetime.datetime.now().strftime('%Y-%m-%d')}"
            save_directory = os.path.join(parent_dicteroy, folder_name); os.makedirs(save_directory, exist_ok=True)

            confirm = True
            window['confirm'].update('Confirmed', text_color='green')
        else:
            if not confirm:
                # get warning window popup
                sg.popup_error('Please confirm the recording devices and playback devices first.')
                continue
            else:
                if event == 'Redo':
                    transcript_count -= 1

                if event == 'Start Recording' and not isRecording:
                    isRecording = True                    

                    duration = int(values['recording_time'])
                    transcript = transcripts[transcript_count].split()[1:]
                    window['content'].update('阅读内容：' + ''.join(transcript))

                    record_command = 'python utils/Audio/record.py --dataset_folder {} --device {} --duration {}'.format(save_directory, record_index, duration)

                    probe_signal = window['proble_signal'].get()[0]
                    if probe_signal == 'none':
                        play_command = 'echo "No probe signal selected, skipping playback."'
                    else:
                        probe_file = f"loggers/{probe_signal}.wav"
                        play_command = 'python utils/Audio/play.py --play_file {} --device {} --duration {}'.format(probe_file, play_index, duration+1)
                    play_process = subprocess.Popen(play_command, shell=True)
                    record_process = subprocess.Popen(record_command, shell=True)
                    threading.Thread(target=countdown_timer, args=(duration, window), daemon=True).start()

                    transcript_count += 1
                    log_file = f"{save_directory}/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
                    log = {
                        'sensor_type': sensor_type[0],
                        'speaker_type': speaker_type[0],
                        'probe_signal': probe_signal,
                        'volunteer': volunteer_name,
                        'recording_time': duration,
                        'transcript': ''.join(transcript),
                    }
                    pd.DataFrame([log]).to_csv(log_file, index=False)
                    
if __name__ == '__main__':
    pass