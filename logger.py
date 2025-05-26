from loggers.location_logger import init_layout_location, record_location
from loggers.speech_logger import init_layout_speech, record_speech
import PySimpleGUI as sg

if __name__ == "__main__":
    sg.set_options(suppress_raise_key_errors=False, suppress_error_popups=False, suppress_key_guessing=False)

    '''
    Main function to initialize the GUI and start the location logging process.
    '''
    # layout = init_layout_location()
    # window = sg.Window("Experiment Setup Logger", layout)
    # record_location(window, layout)

    '''
    Main function to initialize the GUI and start the speech logging process.
    '''
    layout = init_layout_speech()
    window = sg.Window("Audio Recording Tool", layout)
    record_speech(window)

