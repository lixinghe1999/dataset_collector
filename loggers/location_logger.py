import FreeSimpleGUI as sg
import datetime
import pandas as pd
import os
import threading
import time
from utils.Audio.dataset import audio_sample
from utils.Audio.play import audio_prepare, chirp_play

def audio_play(sources, duration=5, sr=44100, db=-8):
    speaker_sources = [source for source in sources if source["type"] == "speaker"]
    if len(speaker_sources) == 0:
        return
    audio_samples = audio_sample("TIMIT", len(speaker_sources))
    audio_samples += [None] * (2 - len(speaker_sources))
    assert len(audio_samples) <= 2
    left_name, right_name = audio_samples
    stereo_audio = audio_prepare(left_name, right_name, int(duration * sr), sr, db)
    chirp_play(stereo_audio, 48000, False)

def create_input_row(font_size, key_prefix):
    return [
        sg.InputText(size=(15, 1), font=('Helvetica', font_size), key=f'{key_prefix}_type'),
        sg.InputText(size=(15, 1), font=('Helvetica', font_size), key=f'{key_prefix}_location'),
        sg.InputText(size=(15, 1), font=('Helvetica', font_size), key=f'{key_prefix}_orientation'),
        sg.InputText(size=(15, 1), font=('Helvetica', font_size), key=f'{key_prefix}_identity'),
        sg.InputText(size=(15, 1), font=('Helvetica', font_size), key=f'{key_prefix}_voice'),
        sg.Button("Delete", font=('Helvetica', font_size), size=(15, 1), key=f'delete_{key_prefix}')
    ]

def countdown_timer(seconds, window):
    for remaining in range(seconds, 0, -1):
        window['remaining_time'].update(f'Time Remaining: {remaining} seconds')
        time.sleep(1)
    window['remaining_time'].update('')  # Reset after countdown

font_size = 14
def init_layout_location():
    input_rows = [create_input_row(font_size, 0)]

    layout = [
        [sg.Text("Source type refers to device id (01, 02) or loudspeaker id (left, right)", font=('Helvetica', font_size), size=(60, 1))],
        [sg.Text("The first source is typically at (0, 0) with 90 degrees orientation.", font=('Helvetica', font_size), size=(60, 1))],
        [sg.Text("Recording time:", font=('Helvetica', font_size), size=(15, 1)),     
        sg.InputText(size=(15, 1), font=('Helvetica', font_size), key='recording_time'),
        sg.Text("", size=(30, 1), font=('Helvetica', font_size), text_color='red', key='remaining_time')],
        [sg.Text("Source Type", font=('Helvetica', font_size), size=(15, 1)), 
        sg.Text("Location (X, Y)", font=('Helvetica', font_size), size=(15, 1)),
        sg.Text("Orientation", font=('Helvetica', font_size), size=(15, 1)),   
        sg.Text("Identity", font=('Helvetica', font_size), size=(15, 1)),
        sg.Text("Voice", font=('Helvetica', font_size), size=(15, 1))],
        *input_rows,
        [sg.Button("Add Row", font=('Helvetica', font_size), size=(15, 1)), 
        sg.Button("Record", font=('Helvetica', font_size), size=(15, 1)), 
        sg.Button("Exit", font=('Helvetica', font_size), size=(15, 1))]
    ]
    return layout

def record_location(window):
    row_counter = 1
    sources = []
    while True:
        event, values = window.read(timeout=100)  # Add timeout to allow the window to refresh

        if event == sg.WINDOW_CLOSED or event == "Exit":
            break
        
        if event == "Add Row":
            new_row = create_input_row(font_size, row_counter)
            row_counter += 1
            window.extend_layout(window, [new_row])
        
        if event.startswith("delete_"):
            row_key = event.split("_")[1]
            window[f'{row_key}_type'].update('')
            window[f'{row_key}_location'].update('')
            window[f'{row_key}_orientation'].update('')
            window[f'{row_key}_identity'].update('')

        if event == "Record":
            try:
                recording_time = int(values['recording_time'])  # Get recording time in seconds
                if recording_time <= 0:
                    sg.popup("Warning", "Please enter a valid recording time.")
                    continue
                
                threading.Thread(target=countdown_timer, args=(recording_time, window), daemon=True).start()

                # Gather all values from the input fields
                sources = []
                for i in range(row_counter):
                    row_data = [window[f'{i}_type'].Get(), window[f'{i}_location'].Get(), 
                                window[f'{i}_orientation'].Get(), window[f'{i}_identity'].Get(), 
                                window[f'{i}_voice'].Get()]
                    if row_data[0]:
                        sources.append({
                            "type": row_data[0],
                            "location": row_data[1],
                            "orientation": row_data[2],
                            "identity": row_data[3],
                            "voice": row_data[4],
                            "time": recording_time
                        })
                
                if sources:
                    start_time = datetime.datetime.now()
                    date_folder = start_time.strftime('%Y-%m-%d')
                    save_file = start_time.strftime('%Y-%m-%d_%H-%M-%S-%f')
                    directory = f'dataset/log/{date_folder}'
                    os.makedirs(directory, exist_ok=True)
                    
                    file_path = f'{directory}/{save_file}.csv'
                    dataframe = pd.DataFrame(sources)
                    dataframe.to_csv(file_path, index=False)
                    audio_play(sources)
                    sg.popup("Success", "Experiment setup log saved successfully!")
                else:
                    sg.popup("Warning", "No sources to save.")
            except ValueError:
                sg.popup("Warning", "Please enter a valid number for recording time.")

    window.close()
