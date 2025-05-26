
import os
import datetime
import PySimpleGUI as sg
import random
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.Audio.record import get_device_index_by_name, receive_audio
full_transcript = "loggers/aishell_transcript_v0.8.txt"

def init_layout_speech():
    '''
    Initialize the layout for the GUI.
    '''
    font_size = 14
    sensor_type = ['knowles', 'ai-micro', 'desktop', 'Yundea']
    # convert to a selectable list in gui (multiple choices)
    sensor_type = [sg.Listbox(sensor_type, size=(80, 4), key='sensor', default_values=[], select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE )]

    speaker_type = ['desktop', 'bluetooth-openmove']
    speaker_type = [sg.Listbox(speaker_type, size=(40, 4), key='speaker', default_values=[], select_mode=sg.LISTBOX_SELECT_MODE_SINGLE )]

    layout = [
        [sg.Text('Recording devices (multi-choices)', font=('Helvetica', font_size), justification='center')],
        sensor_type,
        [sg.Text('Playback devices (single-choice)', font=('Helvetica', font_size), justification='center')],
        speaker_type,
        [sg.Text("Volunteer Name:",  font=('Helvetica', font_size), size=(font_size, 1)), sg.InputText(size=(font_size, 1), key='volunteer', default_text='Lixing_He')],
        # add recording time input
        [sg.Text("Recording time:", font=('Helvetica', font_size), size=(15, 1)),     
        sg.InputText(size=(15, 1), font=('Helvetica', font_size), key='recording_time'),
        sg.Text("", size=(30, 1), font=('Helvetica', font_size), text_color='red', key='remaining_time')],
        [sg.Button('Confirm', font=('Helvetica', font_size), size=(font_size, 1))],
        # add a text box to show the content to be read
        [sg.Text('阅读内容：', font=('Helvetica', font_size), size=(15, 1), key='content')],
        [sg.Button('Start Recording', font=('Helvetica', font_size), size=(font_size, 1))],
        [sg.Button('Redo', font=('Helvetica', font_size), size=(font_size, 1))],
        [sg.Button('Stop Recording', font=('Helvetica', font_size), size=(font_size, 1))],
        [sg.Button('Exit',  font=('Helvetica', font_size), size=(font_size, 1))]
    ]
    return layout


def record_parser(sensor_type):
    print('Selected sensor type:', sensor_type)
    if len(sensor_type) == 0:
        print('No sensor selected, please select at least one sensor.')
        return None
    for sensor in sensor_type:
        device_index, device_name = get_device_index_by_name(sensor)
        print(f'Using device index: {device_index}, device name: {device_name}')
    # return the function to receive audio 
    def receive_audio_wrapper(dataset_folder, duration=5):
        '''
        Wrapper function to receive audio data from the selected sensors.
        '''
        receive_audio(dataset_folder, sensor_type, duration)
    return receive_audio_wrapper

def playback_parser(speaker_type):
    print('Selected speaker type:', speaker_type)
    if len(speaker_type) == 0:
        print('No speaker selected, please select a speaker.')
        return None
    for speaker in speaker_type:
        device_index, device_name = get_device_index_by_name(speaker)
        print(f'Using device index: {device_index}, device name: {device_name}')
    # return the function to play audio
    def play_audio_wrapper(audio_file):
        '''
        Wrapper function to play audio data on the selected speakers.
        '''
        audio_play(speaker_type, audio_file)
    return play_audio_wrapper

def record_speech(window):
    transcripts = open(full_transcript, 'r', encoding='utf-8').readlines()
    len_transcripts = len(transcripts)
    print('load transcripts with length of:', len_transcripts)
    parent_dicteroy = 'recordings'

    recording = False
    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED or event == 'Exit': # if user closes window or clicks cancel
             break
        if event == 'Confirm':
            sensor_type = window['sensor'].get()
            record_func = record_parser(sensor_type)

            speaker_type = window['speaker'].get()
            play_func = playback_parser(speaker_type)

            volunteer_name = window['volunteer'].get()
            folder_name = f"{volunteer_name}_{datetime.datetime.now().strftime('%Y-%m-%d')}"
            parent_dicteroy = os.path.join(parent_dicteroy, folder_name); os.makedirs(parent_dicteroy, exist_ok=True)

        if event == 'Redo' and recording == False:
            # remove the previous recording
            start_time = datetime.datetime.now()
            fname = start_time.time().strftime("%H_%M_%S")
            window['content'].update('阅读内容：' + ''.join(transcript))

            recording = True
        if event == 'Start Recording' and recording == False:
            start_time = datetime.datetime.now()
            fname = start_time.time().strftime("%H_%M_%S")
            index = random.randint(0, len_transcripts-1)
            transcript = transcripts[index].split()[1:]

            window['content'].update('阅读内容：' + ''.join(transcript))
            recording = True
        if event == 'Stop Recording' and recording == True:
            window['content'].update('录制完成')
            recording = False

    # date = datetime.datetime.now().date()
    # parent_dicteroy = os.path.join(args.sensor, args.volunteer, str(date))

    # if not os.path.exists(parent_dicteroy):
    #     os.makedirs(parent_dicteroy)
    # if args.sensor == 'arduino':
    #     start = getattr(receive_arduino, 'start')
    #     record = getattr(receive_arduino, 'record')
    # else:
    #     start = getattr(receive_knowles, 'start')
    #     record = getattr(receive_knowles, 'record')
    # recording = False
    # labels = []
    # time_sum = 0
    # while True:
    #     event, values = window.read()
    #     if event == '重做' and recording == False:
    #         # remove the previous recording
    #         os.remove(os.path.join(parent_dicteroy, fname + '.wav'))

    #         start_time = datetime.datetime.now()
    #         fname = start_time.time().strftime("%H_%M_%S")
    #         start()
    #         window['content'].update('阅读内容：' + ''.join(transcript))

    #         recording = True
    #     if event == '相关度' and recording == False:
    #         metric = stats_metric(os.path.join(parent_dicteroy, fname + '.wav'))
    #         window['correlation'].update(metric)

    #     if event == '开始' and recording == False:
    #         start_time = datetime.datetime.now()
    #         fname = start_time.time().strftime("%H_%M_%S")
    #         index = random.randint(0, len_transcripts-1)
    #         transcript = transcripts[index].split()[1:]
    #         labels.append(' '.join([fname] + transcript))
    #         start()
    #         window['content'].update('阅读内容：' + ''.join(transcript))
    #         recording = True
    #     if event == '完成' and recording == True:
    #         duration = (datetime.datetime.now() - start_time).total_seconds()
    #         record(os.path.join(parent_dicteroy, fname + '.wav'), int(duration)+1, plot=False)
    #         window['content'].update('录制完成')
    #         time_sum += duration
    #         window['time'].update('采集时间:' + str(time_sum))
    #         recording = False
    #     if event == sg.WIN_CLOSED or event == '结束': # if user closes window or clicks cancel
    #         break

    # if os.path.exists(os.path.join(parent_dicteroy, 'labels.txt')):
    #     if labels == []:
    #         pass
    #     else:
    #         open(os.path.join(parent_dicteroy, 'labels.txt'), 'a', encoding='utf-8').write('\n' + '\n'.join(labels))
    # else:
    #     open(os.path.join(parent_dicteroy, 'labels.txt'), 'w', encoding='utf-8').write('\n'.join(labels))
    # window.close()

if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Process some integers.')
    # parser.add_argument('--sensor', '-s', action = "store", type=str, default='knowles', required=False)    
    # parser.add_argument('--volunteer', '-v', action = "store", type=str, default='Lixing_He', required=False)    
    # args = parser.parse_args()
    # transcripts = open(full_transcript, 'r', encoding='utf-8').readlines()
    # len_transcripts = len(transcripts)

    # date = datetime.datetime.now().date()
    # parent_dicteroy = os.path.join(args.sensor, args.volunteer, str(date))

    # if not os.path.exists(parent_dicteroy):
    #     os.makedirs(parent_dicteroy)
    # if args.sensor == 'arduino':
    #     start = getattr(receive_arduino, 'start')
    #     record = getattr(receive_arduino, 'record')
    # else:
    #     start = getattr(receive_knowles, 'start')
    #     record = getattr(receive_knowles, 'record')

    layout = init_layout()
    window = sg.Window('Audio Recording Tool', layout, size=(800, 400))
    speech_gui(window)    
    