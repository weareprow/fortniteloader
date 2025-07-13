import os
import shutil
import json
import urllib.request
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import io

# --- Constants ---
CONFIG_FILE = "config.json"
TARGET_SUBDIR = os.path.join("Saved", "PersistentDownloadDir", "CMS", "Files", "C28FF1DE0C661DAF01E118A30B3F21B897A7A6E2")

# --- Fonts ---
FONT_LARGE = ("Segoe UI", 22, "bold")
FONT_MEDIUM = ("Segoe UI", 16)
FONT_SMALL = ("Segoe UI", 13)

# --- Config ---
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)

config = load_config()

# --- Appearance ---
ctk.set_appearance_mode(config.get("theme", "Dark").capitalize())
ctk.set_default_color_theme("dark-blue")

# --- App Setup ---
app = ctk.CTk()
app.title("Fortnite Loader")
app.geometry("900x580")
app.resizable(False, False)

# --- Logger ---
def log(msg):
    ts = datetime.now().strftime("[%H:%M:%S]")
    if 'console' in globals():
        console.insert("end", f"{ts} {msg}\n")
        console.see("end")
    print(f"{ts} {msg}")

# --- Utilities ---
def get_target_path():
    return os.path.join(config.get("game_path", ""), TARGET_SUBDIR)

def validate_base():
    base = config.get("base_dir", "")
    return all(os.path.isdir(os.path.join(base, name)) for name in ["loader", "backup"])

# --- File Actions ---
def make_backup():
    tgt = get_target_path()
    if not os.path.exists(tgt):
        log("Target folder not found.")
        return
    os.makedirs(config["backup_dir"], exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bkp = os.path.join(config["backup_dir"], f"backup_{ts}")
    shutil.copytree(tgt, bkp)
    log(f"Backup created: {bkp}")

def copy_folder(src):
    tgt = get_target_path()
    shutil.rmtree(tgt, ignore_errors=True)
    os.makedirs(os.path.dirname(tgt), exist_ok=True)
    shutil.copytree(src, tgt)
    log(f"Copied from {src} to game")

def load_loader():
    if not config.get("game_path") or not config.get("loader_path"):
        log("Game or loader path not set")
        return
    make_backup()
    copy_folder(config["loader_path"])

def fabio_mode():
    if not config.get("game_path") or not config.get("fabio_path"):
        log("Fabio path not set")
        messagebox.showerror("Error", "Fabio folder not found.")
        return
    make_backup()
    copy_folder(config["fabio_path"])

def reset_to_default():
    tgt = get_target_path()
    if not os.path.exists(tgt):
        log("Nothing to reset.")
        return
    if messagebox.askyesno("Confirm", "Delete all files from game folder?"):
        shutil.rmtree(tgt)
        log("Game folder reset.")

def sync_loader():
    tgt = get_target_path()
    count = 0
    for root, _, files in os.walk(tgt):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, tgt)
            dst = os.path.join(config["loader_path"], rel)
            if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                count += 1
                log(f"Synced: {rel}")
    log(f"Sync complete: {count} files")

def load_backup():
    folder = filedialog.askdirectory(title="Select backup folder")
    if folder and os.listdir(folder):
        if messagebox.askyesno("Load Backup", f"Load from {folder}?"):
            copy_folder(folder)

def launch_fn():
    try:
        os.startfile("com.epicgames.launcher://apps/Fortnite?action=launch&silent=true")
        log("Fortnite launched")
    except Exception as e:
        log(f"Launch failed: {e}")
        messagebox.showerror("Error", str(e))

def toggle_theme():
    mode = "Light" if ctk.get_appearance_mode() == "Dark" else "Dark"
    ctk.set_appearance_mode(mode)
    config["theme"] = mode.lower()
    save_config(config)

# --- Setup ---
def setup_complete():
    return config.get("game_path") and config.get("base_dir") and validate_base()

def update_setup():
    step1_lbl.configure(text=f"Step 1: Select FortniteGame folder. {'✅' if config.get('game_path') else '❌'}")
    step2_lbl.configure(text=f"Step 2: Select Base folder. {'✅' if config.get('base_dir') and validate_base() else '❌'}")
    enabled = setup_complete()
    for b in sidebar_buttons:
        b.configure(state="normal" if enabled else "disabled")
    switch_to(main if enabled else wizard_frame)
    if enabled:
        log("Setup complete.")

# --- Folder Selection ---
def select_game_folder():
    path = filedialog.askdirectory(title="Select FortniteGame folder")
    if not path:
        return
    if os.path.basename(path) == "FortniteGame":
        target = os.path.join(path, TARGET_SUBDIR)
        if os.path.exists(target):
            config["game_path"] = path
            save_config(config)
            log(f"Game folder set: {path}")
            update_setup()
        else:
            messagebox.showerror("Error", f"Missing folder:\n{TARGET_SUBDIR}")
    else:
        messagebox.showerror("Error", "Selected folder must be 'FortniteGame'")

def select_base_folder():
    path = filedialog.askdirectory(title="Select base folder")
    if not path:
        return
    loader = os.path.join(path, "loader")
    fabio = os.path.join(path, "Fabio")
    if os.path.isdir(loader):
        config.update({
            "base_dir": path,
            "loader_path": loader,
            "fabio_path": fabio if os.path.isdir(fabio) else "",
            "backup_dir": os.path.join(path, "backup")
        })
        save_config(config)
        log(f"Base folder set: {path}")
        update_setup()
    else:
        messagebox.showerror("Error", "Base folder must contain a 'loader' folder")

# --- UI Layout ---
sidebar = ctk.CTkFrame(app, width=200, fg_color="#1F1F1F", corner_radius=0)
sidebar.pack(side="left", fill="y")

main = ctk.CTkFrame(app)
settings = ctk.CTkFrame(app)
console_frame = ctk.CTkFrame(app)
wizard_frame = ctk.CTkFrame(app)
fabio_frame = ctk.CTkFrame(app)
for f in [main, settings, console_frame, wizard_frame, fabio_frame]:
    f.pack_forget()

current_frame = None
sidebar_buttons = []

logo = None
try:
    with urllib.request.urlopen("https://res.cloudinary.com/ddzbf2c9o/image/upload/v1752426644/12840ico_on7j3l.png") as u:
        logo = ctk.CTkImage(Image.open(io.BytesIO(u.read())), size=(128, 40))
except Exception as e:
    log(f"Logo failed: {e}")

if logo:
    ctk.CTkLabel(sidebar, image=logo, text="").pack(pady=(30, 10))
else:
    ctk.CTkLabel(sidebar, text="Fortnite Loader", font=FONT_LARGE).pack(pady=(30, 10))

ctk.CTkLabel(sidebar, text="Dashboard", font=("Segoe UI", 16, "bold"), text_color="#00BFFF").pack(pady=(10, 20))

def sidebar_button(text, command):
    btn = ctk.CTkButton(
        sidebar, text=text, command=command,
        font=("Segoe UI", 14), corner_radius=12,
        height=40, width=160, fg_color="#2A2A2A",
        hover_color="#444", text_color="white")
    return btn

sidebar_buttons.extend([
    sidebar_button("🏠 Main", lambda: switch_to(main)),
    sidebar_button("⚙️ Settings", lambda: switch_to(settings)),
    sidebar_button("📝 Console", lambda: switch_to(console_frame)),
    sidebar_button("🦾 Fabio", lambda: switch_to(fabio_frame)),
])

for btn in sidebar_buttons:
    btn.pack(pady=8, padx=20)

ctk.CTkLabel(sidebar, text=" ", height=30).pack()
ctk.CTkButton(
    sidebar, text="🚀 Launch Fortnite", command=launch_fn,
    font=("Segoe UI", 14, "bold"), corner_radius=20,
    height=45, width=160, fg_color="#0078D7",
    hover_color="#005A9E", text_color="white"
).pack(pady=30, padx=20, side="bottom")

def switch_to(f):
    global current_frame
    if not setup_complete() and f != wizard_frame:
        messagebox.showinfo("Setup required", "Please complete setup first.")
        return
    if current_frame:
        current_frame.pack_forget()
    f.pack(fill="both", expand=True)
    current_frame = f

# --- Main ---
ctk.CTkLabel(main, text="👨\u200d🔧 Game ↔ Loader", font=FONT_LARGE).pack(pady=30)
for t, cmd in [
    ("📅 Load Loader → Game", load_loader),
    ("🔁 Sync Game → Loader", sync_loader),
    ("🗂️ Load Backup", load_backup),
    ("🔄 Reset to Default", reset_to_default),
]:
    ctk.CTkButton(main, text=t, command=cmd, height=40, width=240, font=FONT_MEDIUM).pack(pady=10)

# --- Settings ---
ctk.CTkLabel(settings, text="⚙️ Settings", font=FONT_LARGE).pack(pady=30)
for t, cmd in [
    ("📂 Select Game Folder", select_game_folder),
    ("📁 Select Base Folder", select_base_folder),
    ("🌗 Toggle Theme", toggle_theme),
]:
    ctk.CTkButton(settings, text=t, command=cmd, height=40, width=240, font=FONT_MEDIUM).pack(pady=10)

# --- Wizard ---
ctk.CTkLabel(wizard_frame, text="🔧 Setup Wizard", font=FONT_LARGE).pack(pady=30)
step1_lbl = ctk.CTkLabel(wizard_frame, text="Step 1: Select FortniteGame folder. ❌", font=FONT_MEDIUM)
step1_lbl.pack(pady=5)
ctk.CTkButton(wizard_frame, text="📂 Select Game Folder", command=select_game_folder).pack(pady=5)
step2_lbl = ctk.CTkLabel(wizard_frame, text="Step 2: Select Base folder. ❌", font=FONT_MEDIUM)
step2_lbl.pack(pady=5)
ctk.CTkButton(wizard_frame, text="📁 Select Base Folder", command=select_base_folder).pack(pady=5)

# --- Console ---
console = ctk.CTkTextbox(console_frame, font=("Courier", 14), wrap="word")
console.pack(fill="both", expand=True, padx=20, pady=20)

# --- Fabio ---
ctk.CTkLabel(fabio_frame, text="🦾 Fabio Mode", font=FONT_LARGE).pack(pady=30)
ctk.CTkButton(fabio_frame, text="🦄 FABIO MODE", command=fabio_mode, height=40, width=240, font=FONT_MEDIUM).pack(pady=10)
ctk.CTkButton(fabio_frame, text="🔄 Reset to Default", command=reset_to_default, height=40, width=240, font=FONT_MEDIUM).pack(pady=10)

# --- Start ---
if not setup_complete():
    app.after(100, update_setup)
else:
    switch_to(main)
    log("FortniteLoader started")

app.mainloop()
