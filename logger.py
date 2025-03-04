import PySimpleGUI as sg
import datetime
import pandas as pd
import os
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

# Function to create a new line of input fields
def create_input_row(font_size, key_prefix):
    return [sg.InputText(size=(15, 1), font=('Helvetica', font_size), key=f'{key_prefix}_type'),
            sg.InputText(size=(15, 1), font=('Helvetica', font_size), key=f'{key_prefix}_location'),
            sg.InputText(size=(15, 1), font=('Helvetica', font_size), key=f'{key_prefix}_orientation'),
            sg.InputText(size=(15, 1), font=('Helvetica', font_size), key=f'{key_prefix}_identity'),
            sg.InputText(size=(15, 1), font=('Helvetica', font_size), key=f'{key_prefix}_voice'),
            sg.Button("Delete", font=('Helvetica', font_size), size=(15, 1), key=f'delete_{key_prefix}')]

# Set the font size parameter
font_size = 14

# Initialize input rows
input_rows = [create_input_row(font_size, 0)]

# Adjusted initial layout with larger text
layout = [
    [sg.Text("Source type refers to device id (01, 02) or loudspeaker id (left, right)", font=('Helvetica', font_size), size=(60, 1))],
    [sg.Text("The first source is typically at (0, 0) with 90 degrees orientation.", font=('Helvetica', font_size), size=(60, 1))],
    [sg.Text("Source Type", font=('Helvetica', font_size), size=(15, 1)), 
     sg.Text("Location (X, Y)", font=('Helvetica', font_size), size=(15, 1)),
     sg.Text("Orientation", font=('Helvetica', font_size), size=(15, 1)),   
     sg.Text("Identity", font=('Helvetica', font_size), size=(15, 1)),
     sg.Text("Voice", font=('Helvetica', font_size), size=(15, 1))],
    *input_rows,  # Initial row of inputs
    [sg.Button("Add Row", font=('Helvetica', font_size), size=(15, 1)), 
     sg.Button("Record", font=('Helvetica', font_size), size=(15, 1)), 
     sg.Button("Exit", font=('Helvetica', font_size), size=(15, 1))]
]

# Create the window
window = sg.Window("Experiment Setup Logger", layout)

# Event loop
row_counter = 1  # To keep track of row keys
sources = []
while True:
    event, values = window.read()
    
    if event == sg.WINDOW_CLOSED or event == "Exit":
        break
    
    if event == "Add Row":
        new_row = create_input_row(font_size, row_counter)
        row_counter += 1
        window.extend_layout(window, [new_row])
    
    if event.startswith("delete_"):
        row_key = event.split("_")[1]
        # delete the content of the row
        window[f'{row_key}_type'].update('')
        window[f'{row_key}_location'].update('')
        window[f'{row_key}_orientation'].update('')
        window[f'{row_key}_identity'].update('')

    if event == "Record":
        # Gather all values from the input fields
        values = [window[key].Get() for key in window.AllKeysDict if key.endswith('_type')]
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
                    "voice": row_data[4]
                })
        
        # Save to CSV
        if sources:
            start_time = datetime.datetime.now()
            date_folder = start_time.strftime('%Y-%m-%d')
            save_file = start_time.strftime('%Y-%m-%d_%H-%M-%S-%f')
            directory = f'dataset/log/{date_folder}'
            os.makedirs(directory, exist_ok=True)  # Create folder if it doesn't exist
            
            file_path = f'{directory}/{save_file}.csv'
            dataframe = pd.DataFrame(sources)
            dataframe.to_csv(file_path, index=False)
            audio_play(sources)
            sg.popup("Success", "Experiment setup log saved successfully!")
        else:
            sg.popup("Warning", "No sources to save.")

# Close the window
window.close()