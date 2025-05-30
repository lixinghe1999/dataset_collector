
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
from utils.Audio.record import get_device_index_by_name, receive_audio

full_transcript = "loggers/aishell_transcript_v0.8.txt"

def init_layout_speech():
    '''
    Initialize the layout for the GUI.
    '''
    font_size = 14
    sensor_type = ['KN BPs USB', 'RØDE AI-Micro', 'USB Advanced Audio Device', 'default']
    # convert to a selectable list in gui (multiple choices)
    sensor_type = [sg.Listbox(sensor_type, size=(80, 4), key='sensor', default_values=['default'], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE )]

    speaker_type = ['AirPods Pro #2 Stereo', 'OpenMove by Shokz', 'none']
    speaker_type = [sg.Listbox(speaker_type, size=(40, 4), key='speaker', default_values=['none'], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE),
                    sg.Listbox(['chirp_16k_20k', 'test', 'none'], size=(40, 4), key='proble_signal', default_values=['test'], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)]

    layout = [
        [sg.Text('Recording devices (multi-choices)', font=('Helvetica', font_size), justification='center')],
        sensor_type,
        [sg.Text('Playback devices (single-choice), if Yes, at least one probe signal is required', font=('Helvetica', font_size), justification='center')],
        speaker_type,
        [sg.Listbox(['left', 'right', 'mono'], size=(40, 3), key='channel', default_values=['mono'], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)],
        [sg.Text("Volunteer Name:",  font=('Helvetica', font_size), size=(font_size, 1)), sg.InputText(size=(font_size, 1), key='volunteer', default_text='LixingHe')],
        # [sg.Text("Recording time:", font=('Helvetica', font_size), size=(15, 1)),     
        #     sg.InputText(size=(15, 1), font=('Helvetica', font_size), key='recording_time', default_text='8'),
        #     sg.Text("", size=(30, 1), font=('Helvetica', font_size), text_color='red', key='remaining_time')],

        [sg.Button('Confirm', font=('Helvetica', font_size), key='confirm', size=(15, 1)), sg.Text('Not confirmed', size=(20, 1), key='confirm_text', font=('Helvetica', font_size), text_color='red')],
        
        [sg.Button('Start Playing', font=('Helvetica', font_size), key="start_play", size=(20, 1), button_color=('white', 'green')),
         sg.Button('Stop Playing', font=('Helvetica', font_size), key="stop_play", size=(20, 1))],
        [sg.Button('Start Recording', font=('Helvetica', font_size), key="start_record", size=(20, 1), button_color=('white', 'green')),
            sg.Button('Stop Recording', font=('Helvetica', font_size), key="stop_record", size=(20, 1))],

        
        [sg.Button('Start Reading', font=('Helvetica', font_size), key="start_read", size=(20, 1)),
         sg.Button('Stop Reading', font=('Helvetica', font_size), key="stop_read", size=(20, 1))],

        [sg.Button('Redo', font=('Helvetica', font_size), key='redo', size=(font_size, 1))],

        [sg.Text('Please read the below content: ', font=('Helvetica', font_size), size=(60, 2), key='content')],
        [sg.Button('Exit',  font=('Helvetica', font_size), key='exit', size=(font_size, 1))]
    ]
    return layout

def device_parser(device_type, record=True):
    print('Selected device type:', device_type)
    if len(device_type) == 0:
        print('No device selected, please select at least one device.')
        return None
    device_indexs = []
    for device in device_type:
        device_index, device_name = get_device_index_by_name(device, record=record)
        print(f'Using device index: {device_index}, device name: {device_name}')
        device_indexs.append(device_index)
    return device_indexs
    
global isRecording
isRecording = False

def countdown_timer(seconds, window):
    global isRecording
    # update the start_record button to stop recording
    window['start_record'].update('Recording...', disabled=True, button_color=('white', 'red'))
    for remaining in range(seconds, 0, -1):
        window['remaining_time'].update(f'Time Remaining: {remaining} seconds')
        time.sleep(1)
    window['remaining_time'].update('')  # Reset after countdown
    isRecording = False
    window['start_record'].update('Start Recording', disabled=False, button_color=('white', 'green'))

def record_speech(window):
    global isRecording
    transcripts = open(full_transcript, 'r', encoding='utf-8').readlines()
    parent_dicteroy = 'recording'
    confirm = False
    transcript_count = 0
    t_record = None
    isReading = False
    while True:
        event, values = window.read()
        print(f'Event: {event}, Values: {values}')
        if event == sg.WIN_CLOSED or event == 'exit': # if user closes window or clicks cancel
             break
        if event == 'confirm':
            sensor_type = window['sensor'].get(); speaker_type = window['speaker'].get()
            probe_signal = window['proble_signal'].get()
            if len(sensor_type) == 0 or len(speaker_type) == 0:
                sg.popup_error('Please select at least one recording device and one playback device.')
                window['confirm'].update('not confirmed', text_color='red')
                continue
            elif speaker_type[0] != 'none' and window['proble_signal'].get()[0] == 'none':
                sg.popup_error('Please select a playback signal.')
                window['confirm'].update('not confirmed', text_color='red')
                continue
            else:
                # obtain the recording and playback functions
                record_indexs = device_parser(sensor_type, record=True)
                play_indexs = device_parser(speaker_type, record=False)
                channel = window['channel'].get()[0]
                volunteer_name = window['volunteer'].get()
                folder_name = f"{volunteer_name}_{datetime.datetime.now().strftime('%Y-%m-%d')}"
                save_directory = os.path.join(parent_dicteroy, folder_name); os.makedirs(save_directory, exist_ok=True)

                confirm = True
                window['confirm_text'].update('Confirmed', text_color='green')
        else:
            if not confirm:
                # get warning window popup
                sg.popup_error('Please confirm the recording devices and playback devices first.')
                continue
            else:
                if event == 'redo':
                    transcript_count -= 1
                if event == 'start_play':
                    print(probe_signal, speaker_type, play_indexs, channel)
                    if probe_signal[0] == 'none' or speaker_type[0] == 'none':
                        play_command = 'echo "No probe signal selected, skipping playback."'
                    else:
                        probe_file = f"loggers/{probe_signal[0]}.wav"
                        # play_command = 'python utils/Audio/play.py --play_file {} --device {} --duration {} --channel {}'.format(probe_file, play_indexs[0], duration, channel)
                        play_command = 'python utils/Audio/play.py --play_file {} --device {} --duration {} --channel {}'.format(probe_file, play_indexs[0], -1, channel)

                        play_process = subprocess.Popen(play_command, shell=False)
                        window['start_play'].update('Playing...', disabled=True, button_color=('white', 'red'))
                if event == 'stop_play':
                    if 'play_process' in locals():
                        play_process.terminate()
                        print('Playback stopped.')
                        window['start_play'].update('Start Playing', disabled=False, button_color=('white', 'green'))
                    else:
                        print('No playback process to stop.')
                if event == 'start_record' and not isRecording:
                    isRecording = True
                    t_record = time.time()
                    for record_index in record_indexs:
                        record_command = 'python utils/Audio/record.py --dataset_folder {} --device {} --duration {}'.format(save_directory, record_index, -1)
                        record_process = subprocess.Popen(record_command, shell=False)
                    window['start_record'].update('Recording...', disabled=True, button_color=('white', 'red'))
                    # threading.Thread(target=countdown_timer, args=(duration, window), daemon=True).start()
                if event == 'stop_record' and isRecording:
                    isRecording = False
                    if 'record_process' in locals():
                        record_process.kill()
                        window['start_record'].update('Start Recording', disabled=False, button_color=('white', 'green'))   
                        print('Record stopped.')
                    else:
                        print('No record process to stop.')
                    t_record = None
                if event == 'start_read' and isReading == False:
                    if t_record == None:
                        sg.popup_error('Please start recording first.')
                        continue
                    
                    transcript = transcripts[transcript_count].split()[1:]
                    window['content'].update('阅读内容：' + ''.join(transcript))
                    transcript_count += 1

                    start_read = time.time()
                    isReading = True
                if event == 'stop_read' and isReading == True:
                    isReading = False
                    end_read = time.time()

                    log_file = f"{save_directory}/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
                    log = {
                        'sensor_type': sensor_type,
                        'speaker_type': speaker_type,
                        'probe_signal': probe_signal,
                        'channel': channel,
                        't_record': t_record,
                        'start_read': start_read,
                        'end_read': end_read,
                        'volunteer': volunteer_name,
                        'transcript': ''.join(transcript),
                    }
                    pd.DataFrame([log]).to_csv(log_file, index=False)
                    
if __name__ == '__main__':
    pass