# Je kan script Loader.py noemen ik dat gdn mr hoeft vgm niet

import os
import sys
import json
import vlc
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import customtkinter as ctk

CONFIG_FILE = "config.json"
VIDEO_FOLDER = os.path.join(os.path.dirname(__file__), "videos")
VIDEO_EXTENSIONS = [".mp4", ".mkv", ".avi", ".mov"]

app = ctk.CTk()
app.title("Fortnite Loader")
app.geometry("900x580")
app.resizable(False, False)

config = {}
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE) as f:
        config = json.load(f)

ctk.set_appearance_mode(config.get("theme", "Dark").capitalize())
ctk.set_default_color_theme("dark-blue")

console = None

def log(msg):
    ts = datetime.now().strftime("[%H:%M:%S]")
    print(f"{ts} {msg}")
    if console:
        console.insert("end", f"{ts} {msg}\n")
        console.see("end")

class VideoPlayer:
    def __init__(self, master):
        self.master = master
        self.video_files = [f for f in os.listdir(VIDEO_FOLDER) if any(f.lower().endswith(ext) for ext in VIDEO_EXTENSIONS)]
        if not self.video_files:
            messagebox.showerror("No videos", f"No videos found in '{VIDEO_FOLDER}'")
            return

        self.index = 0
        self.seeking = False
        self.instance = vlc.Instance(['--no-xlib', '--avcodec-hw=none'])
        self.player = self.instance.media_player_new()

        self.canvas = tk.Canvas(master, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, pady=10)

        self.title_label = ttk.Label(master, text=self.video_files[self.index], font=("Segoe UI", 20))
        self.title_label.pack(pady=10)

        control_frame = ttk.Frame(master)
        control_frame.pack(pady=5)

        ttk.Button(control_frame, text="⏯ Play/Pause", command=self.play_pause).grid(row=0, column=0, padx=5)
        ttk.Button(control_frame, text="⏭ Next Video", command=self.next_video).grid(row=0, column=1, padx=5)
        ttk.Button(control_frame, text="⏹ Stop", command=self.stop).grid(row=0, column=2, padx=5)

        self.volume_slider = ttk.Scale(control_frame, from_=0, to=100, command=self.set_volume)
        self.volume_slider.set(50)
        self.volume_slider.grid(row=0, column=3, padx=5)

        self.time_slider = ttk.Scale(master, from_=0, to=1000, orient="horizontal")
        self.time_slider.pack(fill="x", padx=20, pady=5)
        self.time_slider.bind("<Button-1>", self.start_seek)
        self.time_slider.bind("<ButtonRelease-1>", self.end_seek)

        self.load_video()
        self.update_slider()

    def load_video(self):
        media_path = os.path.join(VIDEO_FOLDER, self.video_files[self.index])
        media = self.instance.media_new(media_path)
        self.player.set_media(media)

        self.master.update_idletasks()

        if sys.platform == "win32":
            self.player.set_hwnd(self.canvas.winfo_id())
        elif sys.platform == "darwin":
            self.player.set_nsobject(self.canvas.winfo_id())
        else:
            self.player.set_xwindow(self.canvas.winfo_id())

        self.player.play()
        self.title_label.config(text=self.video_files[self.index])
        self.player.audio_set_volume(int(self.volume_slider.get()))
        self.check_end()

    def play_pause(self):
        if self.player.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def stop(self):
        self.player.stop()

    def next_video(self):
        self.index = (self.index + 1) % len(self.video_files)
        self.load_video()

    def set_volume(self, val):
        self.player.audio_set_volume(int(float(val)))

    def seek(self, val):
        if self.player.get_length() > 0:
            self.player.set_time(int(float(val)/1000 * self.player.get_length()))

    def start_seek(self, event):
        self.seeking = True

    def end_seek(self, event):
        self.seeking = False
        self.seek(self.time_slider.get())

    def update_slider(self):
        if not self.seeking and self.player.get_length() > 0:
            pos = self.player.get_time() / self.player.get_length() * 1000
            self.time_slider.set(pos)
        self.master.after(100, self.update_slider)

    def check_end(self):
        def poll():
            if self.player.get_state() == vlc.State.Ended:
                self.next_video()
            else:
                self.master.after(500, poll)
        poll()

sidebar = ctk.CTkFrame(app, width=200, fg_color="#1F1F1F")
sidebar.pack(side="left", fill="y")

container = ctk.CTkFrame(app)
container.pack(side="right", fill="both", expand=True)

pages = {}
for name in ("main", "settings", "console", "fabio", "fortify", "wizard"):
    frame = ctk.CTkFrame(container)
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    pages[name] = frame

fortify_loaded = False

# Add page content

def add_content(name, text, buttons):
    ctk.CTkLabel(pages[name], text=text, font=("Segoe UI", 22)).pack(pady=30)
    for btn_text, btn_cmd in buttons:
        ctk.CTkButton(pages[name], text=btn_text, command=lambda c=btn_cmd: c(),
                      height=40, width=180, corner_radius=12).pack(pady=10)

add_content("main", "👨‍🔧 Game ↔ Loader", [
    ("Launch Fortnite", lambda: log("Launching Fortnite...")),
    ("Repair Installation", lambda: log("Repairing installation..."))
])

add_content("settings", "⚙️ Settings", [
    ("Save Settings", lambda: log("Settings saved.")),
    ("Reset to Default", lambda: log("Settings reset to default.")),
    ("Change Theme", lambda: log("Theme changed."))
])

add_content("fabio", "🪾 Fabio Mode", [
    ("Activate Fabio", lambda: log("Fabio activated.")),
    ("Deactivate Fabio", lambda: log("Fabio deactivated."))
])

add_content("wizard", "🔧 Setup Wizard", [
    ("Run Wizard", lambda: log("Wizard running...")),
    ("Skip Wizard", lambda: log("Wizard skipped."))
])

# Fortify page with video player and proper buttons
def load_fortify():
    VideoPlayer(pages["fortify"])
    ctk.CTkButton(pages["fortify"], text="Reload Videos", command=lambda: log("Videos reloaded."),
                  height=40, width=180, corner_radius=12).pack(pady=10)
    ctk.CTkButton(pages["fortify"], text="Delete All Videos", command=lambda: log("All videos deleted."),
                  height=40, width=180, corner_radius=12).pack(pady=10)

console = ctk.CTkTextbox(pages["console"], font=("Courier", 13))
console.pack(fill="both", expand=True, padx=20, pady=20)

# Show pages

def show_frame(name):
    global fortify_loaded
    if name == "fortify" and not fortify_loaded:
        load_fortify()
        fortify_loaded = True
    pages[name].tkraise()

for txt, key in [
    ("🏠 Main", "main"),
    ("⚙️ Settings", "settings"),
    ("📝 Console", "console"),
    ("🪾 Fabio", "fabio"),
    ("🎬 Fortify", "fortify"),
]:
    btn = ctk.CTkButton(
        sidebar, text=txt, command=lambda k=key: show_frame(k),
        font=("Segoe UI", 14), corner_radius=12,
        height=40, width=180
    )
    btn.pack(pady=8, padx=10)

ctk.CTkButton(
    sidebar, text="🚀 Launch Fortnite", command=lambda: log("Launching Fortnite..."),
    font=("Segoe UI", 14, "bold"), corner_radius=20,
    height=45, width=180, fg_color="#0078D7"
).pack(pady=30, padx=10, side="bottom")

if not (config.get("game_path") and config.get("base_dir")):
    show_frame("wizard")
else:
    show_frame("main")
    log("Fortnite Loader started")

app.mainloop()
