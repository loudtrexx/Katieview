import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageSequence
import random
import os
import ctypes 
import pyautogui
import json
import shutil


# --- CONFIGURATION ---
config_path = "config.json"
settings_window = None  # Global reference to the settings window
wallpaperapplyfolder = "temp"

def clean_cache(temp_dir):
    shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

def start_timer():
    interval_minutes = interval_var.get()
    if interval_minutes == 0 and custom_var.get().isdigit():
        interval_minutes = int(custom_var.get())

    milliseconds = interval_minutes * 60 * 1000

    if image_list:
        random_image = random.choice(image_list)
        wallpaper_execute(random_image)

    # Schedule next call
    root.after(milliseconds, start_timer)

def stop_timer():
    global timer_id
    if timer_id:
        root.after_cancel(timer_id)
        timer_id = None
        print("Wallpaper rotation stopped.")


def wallpaper_execute(image):
    output_path = fit_wallpaper(image, wallpaperapplyfolder)
    set_wallpaper(image)
    
def save_config(folder_path):
    with open(config_path, 'w') as f:
        json.dump({"folder": folder_path}, f)

def load_config():
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            try:
                return json.load(f).get("folder", "")
            except json.JSONDecodeError:
                return ""
    return ""
# --- WALLPAPER FUNCTIONS ---

def set_wallpaper(image_path):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)

def fit_wallpaper(image_path, output_folder):
    screen_w, screen_h = pyautogui.size()
    img = Image.open(image_path)
    w, h = img.size
    aspect_img = w / h
    aspect_scr = screen_w / screen_h

    if aspect_img > aspect_scr:
        # Image is too wide
        new_h = screen_h
        new_w = int(new_h * aspect_img)
        img = img.resize((new_w, new_h))
        left = (new_w - screen_w) // 2
        img = img.crop((left, 0, left + screen_w, screen_h))
    else:
        # Image is too tall
        new_w = screen_w
        new_h = int(new_w / aspect_img)
        img = img.resize((new_w, new_h))
        top = (new_h - screen_h) // 2
        img = img.crop((0, top, screen_w, top + screen_h))

    # Extract the original filename
    filename = os.path.basename(image_path)
    output_path = os.path.join(output_folder, filename)

    os.makedirs(output_folder, exist_ok=True)
    img.save(output_path)

    return output_path  # Return the new image path


# --- IMAGE LOADING / THUMBNAILS ---

# --- IMAGE LOADING / THUMBNAILS ---

image_list = []  # List to hold image paths

def load_thumbnails(folder):
    global image_list  # Ensure we're modifying the global list

    # Clear any previous widgets or image data
    for widget in thumb_frame.winfo_children():
        widget.destroy()
    thumbnail_refs.clear()
    gif_players.clear()
    image_list.clear()  # Clear the list each time

    exts = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
    files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in exts]

    for idx, fname in enumerate(files):
        path = os.path.join(folder, fname)
        ext = os.path.splitext(fname)[1].lower()
        
        # Add the image to the list of paths
        image_list.append(path)
        print(image_list)

        try:
            if ext == '.gif':
                gif = Image.open(path)
                frames = [ImageTk.PhotoImage(f.copy().resize((100, 100))) for f in ImageSequence.Iterator(gif)]
                lbl = tk.Label(thumb_frame, bg="white")
                lbl.grid(row=idx//5, column=idx%5, padx=5, pady=5)
                def animate(lbl=lbl, frames=frames, i=0):
                    lbl.configure(image=frames[i])
                    i = (i + 1) % len(frames)
                    root.after(100, animate, lbl, frames, i)
                animate()
                gif_players.append(frames)
            else:
                img = Image.open(path)
                img.thumbnail((100, 100))
                tk_img = ImageTk.PhotoImage(img)
                thumbnail_refs.append(tk_img)
                lbl = tk.Label(thumb_frame, image=tk_img, bg="white")
                lbl.grid(row=idx//5, column=idx%5, padx=5, pady=5)
        except Exception as e:
            print(f"Error loading {fname}: {e}")

# Now you can access the `image_list` to see all the image paths from the folder


def change_folder():
    folder = filedialog.askdirectory()
    if folder:
        clean_cache("temp")
        folder_var.set(f'Folder: "{folder}"')
#        save_config(folder)
        load_thumbnails(folder)

# --- SETTINGS WINDOW ---

def open_settings():
    global settings_window
    if settings_window and tk.Toplevel.winfo_exists(settings_window):
        settings_window.lift()
        return

    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x150")
    settings_window.configure(bg="black")

    tk.Label(settings_window, text="Default Folder:", bg="black", fg="white").pack(pady=10)

    preset_var = tk.StringVar(value=load_config())
    entry = tk.Entry(settings_window, textvariable=preset_var, width=40)
    entry.pack()

    def choose_folder():
        folder = filedialog.askdirectory()
        if folder:
            preset_var.set(folder)
            save_config(folder)

    tk.Button(settings_window, text="Browse...", command=choose_folder).pack(pady=5)
    tk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=5)

# --- UI SETUP ---

root = tk.Tk()
root.title("Wallpaper Rotator")
root.configure(bg="black")

# Load saved folder on startup
saved = load_config()
if saved and os.path.isdir(saved):
    folder_var = tk.StringVar(value=f'Folder: "{saved}\\"')
else:
    folder_var = tk.StringVar(value=f'Folder: ')

# --- FOLDER SELECTION ---

folder_frame = tk.Frame(root, bg="black")
folder_frame.pack(pady=10)

change_btn = tk.Button(folder_frame, text="Change folder", command=change_folder)
change_btn.grid(row=0, column=0, padx=5)

folder_entry = tk.Entry(folder_frame, textvariable=folder_var, width=50)
folder_entry.grid(row=0, column=1)

# --- THUMBNAIL PREVIEW ---

preview_frame = tk.Frame(root, bg="white", width=600, height=300)
preview_frame.pack(pady=10)
preview_frame.pack_propagate(False)

canvas = tk.Canvas(preview_frame, bg="white", width=580, height=280)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)

thumb_frame = tk.Frame(canvas, bg="white")
canvas.create_window((0,0), window=thumb_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

thumb_frame.bind("<Configure>", on_frame_configure)

thumbnail_refs = []
gif_players = []

# Load thumbnails if we have a valid folder
if saved and os.path.isdir(saved):
    load_thumbnails(saved)

# --- INTERVAL OPTIONS ---

interval_frame = tk.Frame(root, bg="black")
interval_frame.pack(pady=10)

tk.Label(interval_frame, text="Change wallpaper every...", fg="white", bg="black").pack()

interval_var = tk.IntVar(value=30)
options_frame = tk.Frame(interval_frame, bg="black")
options_frame.pack()

for val in [30, 60, 90]:
    tk.Radiobutton(options_frame, text=str(val), variable=interval_var, value=val,
                   fg="white", bg="black", selectcolor="black").pack(side=tk.LEFT, padx=10)

# --- CUSTOM INTERVAL (with numeric input only) ---

custom_var = tk.StringVar()

def validate_number(P):
    return P.isdigit() or P == ""

vcmd = (root.register(validate_number), '%P')

def select_custom():
    if custom_var.get().isdigit():
        interval_var.set(int(custom_var.get()))
    else:
        interval_var.set(0)

custom_frame = tk.Frame(interval_frame, bg="black")
custom_frame.pack(pady=5)

tk.Radiobutton(custom_frame, text="", variable=interval_var, value=0,
               fg="white", bg="black", selectcolor="black", command=select_custom).pack(side=tk.LEFT)

tk.Label(custom_frame, text="Custom (min):", fg="white", bg="black").pack(side=tk.LEFT)

custom_entry = tk.Entry(custom_frame, textvariable=custom_var, width=5, 
                        validate="key", validatecommand=vcmd)
custom_entry.pack(side=tk.LEFT)
custom_entry.bind("<FocusOut>", lambda e: select_custom())

tk.Label(custom_frame, text="minutes.", fg="white", bg="black").pack(side=tk.LEFT, padx=5)

# --- ACTION BUTTONS ---

btn_frame = tk.Frame(root, bg="black")
btn_frame.pack(pady=10)

apply_btn = tk.Button(btn_frame, text="Apply", width=20, command=start_timer)
apply_btn.pack(side=tk.LEFT, padx=10)

settings_btn = tk.Button(btn_frame, text="Settings...", width=20, command=open_settings)
settings_btn.pack(side=tk.LEFT, padx=10)

# --- MAIN LOOP ---
root.mainloop()