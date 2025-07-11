import os
import shutil
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox, scrolledtext

CONFIG_FILE = "config.json"

# === CONFIG LOAD/SAVE ===
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                cfg = json.load(f)
                return {k: v for k, v in cfg.items() if v}
        except Exception:
            return {}
    return {}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

config = load_config()

# === APP INIT ===
ctk.set_appearance_mode(config.get("theme", "dark"))
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Epic Loader Manager")
app.geometry("1000x640")
app.minsize(800, 600)

# === LOG FUNCTIE ===
def log(message):
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    console.insert("end", f"{timestamp} {message}\n")
    console.see("end")

# === BUTTON STIJL ===
def styled_button(master, text, command):
    return ctk.CTkButton(
        master,
        text=text,
        height=48,
        width=360,
        corner_radius=12,
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color="#202225",
        hover_color="#2f3136",
        text_color="#ffffff",
        border_color="#7289da",
        border_width=2,
        command=command
    )

# === PADEN ===
def kies_game_map():
    folder = filedialog.askdirectory(title="Kies je Game-map (A)")
    if folder:
        config["game_path"] = folder
        save_config(config)
        log(f"Game-map ingesteld op: {folder}")

def kies_basis_map():
    folder = filedialog.askdirectory(title="Kies de basis-map")
    if folder:
        config["base_dir"] = folder
        config["loader_path"] = os.path.join(folder, "loader")
        config["backup_dir"] = os.path.join(folder, "backup")
        save_config(config)
        log(f"Basis-map ingesteld op: {folder}")

def validate_base_folder():
    base = config.get("base_dir", "")
    required = ["loader", "backup", "Loader.py"]
    for name in required:
        path = os.path.join(base, name)
        if name.endswith(".py") and not os.path.isfile(path):
            return False
        elif not name.endswith(".py") and not os.path.isdir(path):
            return False
    return True

# === BACKUP ===
def maak_backup():
    if not config.get("game_path"):
        log("Game-map niet ingesteld.")
        return
    os.makedirs(config["backup_dir"], exist_ok=True)
    tijdcode = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_pad = os.path.join(config["backup_dir"], f"backup_{tijdcode}")
    shutil.copytree(config["game_path"], backup_pad)
    log(f"Backup gemaakt naar: {backup_pad}")

# === OPERATIES ===
def laad_loader_naar_game():
    if not config.get("game_path") or not config.get("loader_path"):
        log("Game-map of Loader-map niet ingesteld.")
        return
    try:
        maak_backup()
        shutil.rmtree(config["game_path"], ignore_errors=True)
        shutil.copytree(config["loader_path"], config["game_path"])
        log("Loader gekopieerd naar Game-map.")
    except Exception as e:
        log(f"Fout bij laden Loader: {e}")

def sync_game_naar_loader():
    if not config.get("game_path") or not config.get("loader_path"):
        log("Game-map of Loader-map niet ingesteld.")
        return
    aantal = 0
    for root, _, files in os.walk(config["game_path"]):
        for file in files:
            src = os.path.join(root, file)
            rel_path = os.path.relpath(src, config["game_path"])
            dst = os.path.join(config["loader_path"], rel_path)
            if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                aantal += 1
                log(f"Gekopieerd: {rel_path}")
    log(f"Sync voltooid: {aantal} bestanden gekopieerd.")

def laad_backup_naar_game():
    folder = filedialog.askdirectory(title="Kies backup-map")
    if not folder or not os.path.isdir(folder):
        log("Geen geldige backup-map gekozen.")
        return
    if not os.listdir(folder):
        log("Backup-map is leeg.")
        return
    if not messagebox.askyesno("Bevestiging", f"Backup laden?\n{folder}"):
        return
    try:
        shutil.rmtree(config["game_path"], ignore_errors=True)
        shutil.copytree(folder, config["game_path"])
        log(f"Backup geladen: {folder}")
    except Exception as e:
        log(f"Fout bij laden backup: {e}")

def toggle_theme():
    mode = "Light" if ctk.get_appearance_mode() == "Dark" else "Dark"
    ctk.set_appearance_mode(mode)
    config["theme"] = mode.lower()
    save_config(config)

# === GUI ===
tab_buttons = ctk.CTkFrame(app, fg_color="#2f3136")
tab_buttons.pack(fill="x")

main_frame = ctk.CTkFrame(app, fg_color="#2b2d31")
settings_frame = ctk.CTkFrame(app, fg_color="#2b2d31")
console_frame = ctk.CTkFrame(app, fg_color="#2b2d31")
for frame in [main_frame, settings_frame, console_frame]:
    frame.pack_forget()

current_frame = None
def switch_to(frame):
    global current_frame
    if current_frame:
        current_frame.pack_forget()
    frame.pack(fill="both", expand=True)
    current_frame = frame

styled_button(tab_buttons, "\ud83e\uddd9 Main", lambda: switch_to(main_frame)).pack(side="left", padx=8, pady=12)
styled_button(tab_buttons, "\u2699\ufe0f Instellingen", lambda: switch_to(settings_frame)).pack(side="left", padx=8, pady=12)
styled_button(tab_buttons, "\ud83d\udcc4 Console", lambda: switch_to(console_frame)).pack(side="left", padx=8, pady=12)

# === MAIN ===
ctk.CTkLabel(main_frame, text="\ud83e\uddd9 Game \u2192 Loader", font=ctk.CTkFont(size=26, weight="bold"), text_color="#ffffff").pack(pady=30)
styled_button(main_frame, "\ud83d\udcc5 Laad Loader \u2192 Game", laad_loader_naar_game).pack(pady=8)
styled_button(main_frame, "\ud83d\udd01 Sync Game \u2192 Loader", sync_game_naar_loader).pack(pady=8)
styled_button(main_frame, "\ud83d\uddc2\ufe0f Laad Backup", laad_backup_naar_game).pack(pady=8)

# === SETTINGS ===
ctk.CTkLabel(settings_frame, text="\u2699\ufe0f Instellingen", font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff").pack(pady=30)
styled_button(settings_frame, "\ud83d\udcc2 Kies Game-map", kies_game_map).pack(pady=6)
styled_button(settings_frame, "\ud83d\udcc1 Kies Basis-map", kies_basis_map).pack(pady=6)
styled_button(settings_frame, "\ud83c\udf17 Toggle Thema", toggle_theme).pack(pady=6)

# === CONSOLE ===
console = scrolledtext.ScrolledText(console_frame, height=20, bg="#1e1e1e", fg="#00ff00")
console.pack(fill="both", expand=True, padx=20, pady=20)

# === SETUP WIZARD ===
class SetupWizard(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Setup Wizard")
        self.geometry("600x400")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()

        self.step = 0
        self.steps = [self.step_game_path, self.step_base_path]
        self.init_ui()

    def init_ui(self):
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.title_label = ctk.CTkLabel(self.frame, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(10, 20))

        self.info_label = ctk.CTkLabel(self.frame, text="", wraplength=500, justify="left")
        self.info_label.pack(pady=(0, 20))

        self.choose_button = styled_button(self.frame, "\ud83d\udcc1 Kies map", self.choose_folder)
        self.choose_button.pack(pady=10)

        self.path_label = ctk.CTkLabel(self.frame, text="Nog geen map gekozen", text_color="#aaaaaa")
        self.path_label.pack(pady=10)

        self.next_button = styled_button(self.frame, "\u23e9 Volgende", self.next_step)
        self.next_button.pack(pady=(20, 0))
        self.next_button.configure(state="disabled")

        self.steps[self.step]()

    def step_game_path(self):
        self.title_label.configure(text="Stap 1: Kies Game-map")
        self.info_label.configure(text="Selecteer waar jouw game is geïnstalleerd.")
        self.choose_type = "game"

    def step_base_path(self):
        self.title_label.configure(text="Stap 2: Kies Basis-map")
        self.info_label.configure(text="Selecteer de map waarin 'loader', 'backup' en 'Loader.py' staan.")
        self.choose_type = "base"

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Kies map")
        if not folder:
            return

        if self.choose_type == "game":
            config["game_path"] = folder
            save_config(config)
        elif self.choose_type == "base":
            config["base_dir"] = folder
            config["loader_path"] = os.path.join(folder, "loader")
            config["backup_dir"] = os.path.join(folder, "backup")
            save_config(config)

        self.path_label.configure(text=folder, text_color="#00ff00")
        self.next_button.configure(state="normal")

    def next_step(self):
        if self.choose_type == "base" and not validate_base_folder():
            self.path_label.configure(text="Ongeldige basis-map.", text_color="red")
            self.next_button.configure(state="disabled")
            return

        self.step += 1
        if self.step < len(self.steps):
            self.next_button.configure(state="disabled")
            self.steps[self.step]()
        else:
            self.destroy()
            log("Setup voltooid.")
            switch_to(main_frame)

# Start wizard bij opstarten als config onvolledig
if not config.get("game_path") or not config.get("base_dir") or not validate_base_folder():
    app.after(100, lambda: SetupWizard(app))
else:
    switch_to(main_frame)
    log("Programma gestart.")

# === START ===
app.mainloop()
