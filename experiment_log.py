import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import datetime
import pandas as pd

from utils.Audio.dataset import audio_sample
from utils.Audio.play import audio_prepare, chirp_play
def audio_play(sources, duration=5, sr=44100, db=-8):
    speaker_sources = [source for source in sources if source["type"] == "speaker"]
    audio_samples = audio_sample("TIMIT", len(speaker_sources))
    audio_samples += [None] * (2 - len(speaker_sources))
    assert len(audio_samples) <= 2
    left_name, right_name = audio_samples
    stereo_audio = audio_prepare(left_name, right_name, int(duration * sr), sr, db)
    chirp_play(stereo_audio, 48000, False)


class SoundSourceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Experiment Setup Logger")
        self.root.geometry("600x300")  # Set the window size to 600x400 pixels

        self.sources = []

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        self.source_listbox = tk.Listbox(self.frame, width=100)
        self.source_listbox.pack()

        self.add_button = tk.Button(self.frame, text="Add Sound Source", command=self.add_source)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(self.frame, text="Delete Sound Source", command=self.delete_source)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.frame, text="Do experiment, will play sound if speaker", command=self.save_log)
        self.save_button.pack(side=tk.LEFT, padx=5)

    def add_source(self):
        source_type = simpledialog.askstring("Input", "Enter source type (speaker/human):")
        if source_type not in ["speaker", "human"]:
            messagebox.showerror("Error", "Invalid source type!")
            return
        
        location = simpledialog.askstring("Input", "Enter location (x,y):")
        if not location:
            return

        orientation = None
        if source_type == "human":
            orientation = simpledialog.askstring("Input", "Enter orientation (degrees):")

        identity = simpledialog.askstring("Input", "Enter identity, name for human, 0/1 for speaker:")

        source_info = {
            "type": source_type,
            "location": location,
            "orientation": orientation,
            "identity": identity
        }
        self.sources.append(source_info)
        self.update_listbox()

    def delete_source(self):
        selected_index = self.source_listbox.curselection()
        if selected_index:
            del self.sources[selected_index[0]]
            self.update_listbox()
        else:
            messagebox.showwarning("Warning", "Select a source to delete.")

    def save_log(self):
        if not self.sources:
            messagebox.showwarning("Warning", "No sources to save.")
            return
        start_time = datetime.datetime.now()
        file_path = 'dataset/log/' + start_time.strftime('%Y%m%d_%H%M%S') + '.csv'
        dataframe = pd.DataFrame(self.sources)
        dataframe.to_csv(file_path, index=False)

        audio_play(self.sources)
        messagebox.showinfo("Success", "Experiment setup log saved successfully!")

    def update_listbox(self):
        self.source_listbox.delete(0, tk.END)
        for source in self.sources:
            info = ""
            for key, value in source.items():
                info += f"{key.capitalize()}: {value} | "
            self.source_listbox.insert(tk.END, info)

if __name__ == "__main__":
    root = tk.Tk()
    app = SoundSourceApp(root)
    root.mainloop()