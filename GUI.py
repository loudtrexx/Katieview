import tkinter as tk 
from tkinter import filedialog, colorchooser
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
import random
import os
import ctypes
import pyautogui
import json
import shutil
import webbrowser
import taskbarmanager

# --- Config and Globals ---
config_path = "config.json"
settings_window = None
wallpaperapplyfolder = "temp"
image_list = []
thumbnail_refs = []
gif_players = []
timer_id = None

# --- Config Load/Save ---
def save_config(folder_path=None, bg_color=None):
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            pass
    if folder_path is not None:
        config["folder"] = folder_path
    if bg_color is not None:
        config["bg_color"] = bg_color
    with open(config_path, 'w') as f:
        json.dump(config, f)

def load_config():
    config = {"folder": "", "bg_color": "black"}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                loaded = json.load(f)
                config.update(loaded)
        except json.JSONDecodeError:
            pass
    return config

def validate_hex_color(color):
    if isinstance(color, str) and color.startswith("#") and len(color) == 7:
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    return False

config = load_config()
bg_color = config.get("bg_color", "#000000")  # Use default if not present

# Fallback to black if the color is invalid
if not validate_hex_color(bg_color):
    print(f"Invalid color '{bg_color}' in config. Falling back to black.")
    bg_color = "#000000"


# --- Load Saved Config ---
config = load_config()
bg_color = config.get("bg_color", "black")
saved_folder = config.get("folder", "")

# --- Utility Functions ---
def clean_cache(temp_dir):
    shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir, exist_ok=True)

def start_timer():
    global timer_id
    interval_minutes = interval_var.get()
    if interval_minutes == 0 and custom_var.get().isdigit():
        interval_minutes = int(custom_var.get())
    milliseconds = interval_minutes * 60 * 1000
    if image_list:
        random_image = random.choice(image_list)
        wallpaper_execute(random_image)
    timer_id = root.after(milliseconds, start_timer)

def stop_timer():
    global timer_id
    if timer_id:
        root.after_cancel(timer_id)
        timer_id = None
        print("Wallpaper rotation stopped.")

def wallpaper_execute(image):
    path = fit_wallpaper(image, wallpaperapplyfolder)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)

def set_wallpaper(image_path):
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 0)

def fit_wallpaper(image_path, output_folder):
    screen_w, screen_h = pyautogui.size()
    img = Image.open(image_path)
    w, h = img.size
    aspect_img = w / h
    aspect_scr = screen_w / screen_h
    if aspect_img > aspect_scr:
        new_h = screen_h
        new_w = int(new_h * aspect_img)
        img = img.resize((new_w, new_h))
        left = (new_w - screen_w) // 2
        img = img.crop((left, 0, left + screen_w, screen_h))
    else:
        new_w = screen_w
        new_h = int(new_w / aspect_img)
        img = img.resize((new_w, new_h))
        top = (new_h - screen_h) // 2
        img = img.crop((0, top, screen_w, top + screen_h))
    
    output_folder = os.path.abspath(output_folder)
    
    # Construct the full output path
    filename = os.path.basename(image_path)
    output_path = os.path.join(output_folder, filename)
    
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Save the image
    img.save(output_path)
    
    # Return the full output path
    return output_path

def load_thumbnails(folder):
    global image_list
    for widget in thumb_frame.winfo_children():
        widget.destroy()
    thumbnail_refs.clear()
    gif_players.clear()
    image_list.clear()
    exts = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
    files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in exts]
    for idx, fname in enumerate(files):
        path = os.path.join(folder, fname)
        ext = os.path.splitext(fname)[1].lower()
        image_list.append(path)
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

def change_folder():
    folder = filedialog.askdirectory()
    if folder:
        clean_cache(wallpaperapplyfolder)
        folder_var.set(f'Folder: "{folder}"')
        load_thumbnails(folder)
        #save_config(folder_path=folder)

def get_text_color(bg_color):
    bg_color = bg_color.lstrip('#')
    if len(bg_color) != 6:
        return "white"  # fallback
    try:
        r, g, b = int(bg_color[0:2], 16), int(bg_color[2:4], 16), int(bg_color[4:6], 16)
    except ValueError:
        return "white"  # fallback on bad hex
    if g > r and g > b:
        return "black"
    luminance = (0.299 * r + 0.587 * g + 0.114 * b)
    return "black" if luminance > 186 else "white"


def change_bg_color():
    color = colorchooser.askcolor()[1]
    if color:
        save_config(bg_color=color)
        apply_background_color(color)

def apply_background_color(color):
    text_color = get_text_color(color)
    root.configure(bg=color)
    if settings_window and tk.Toplevel.winfo_exists(settings_window):
        settings_window.configure(bg=color)

    def update_widgets(widgets):
        for widget in widgets:
            if widget == folder_entry or widget == custom_entry:
                widget.configure(bg="white", fg="black")
                continue
            if isinstance(widget, tk.Button) and widget.cget("bg") == "white" and widget.cget("fg") == "black":
                continue
            if isinstance(widget, (tk.Label, tk.Entry, tk.Radiobutton)):
                widget.configure(fg=text_color)
            if isinstance(widget, (tk.Frame, tk.Label, tk.Entry, tk.Radiobutton)):
                widget.configure(bg=color)

    update_widgets(root.winfo_children())
    if settings_window and tk.Toplevel.winfo_exists(settings_window):
        update_widgets(settings_window.winfo_children())
    update_widgets(interval_frame.winfo_children())
    update_widgets(custom_frame.winfo_children())
    update_widgets(radio_buttons)
    custom_radio.configure(bg=color, fg=text_color)

def open_settings():
    global settings_window
    if settings_window and tk.Toplevel.winfo_exists(settings_window):
        settings_window.lift()
        return
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings - Katieview")
    settings_window.geometry("500x500")
    settings_window.resizable(False, False)
    settings_window.configure(bg=bg_color)
    settings_window.iconphoto(False, icon)

    tk.Label(settings_window, text="Default Folder:", bg=bg_color, fg="white").pack(pady=10)
    folder_frame = tk.Frame(settings_window, bg="white", width=450, height=30)
    folder_frame.pack(pady=10)
    
    preset_var = tk.StringVar(value=saved_folder)
    folder_entry = tk.Entry(folder_frame, textvariable=preset_var, width=40, bg="white", fg="black", bd=0)
    folder_entry.pack(fill=tk.BOTH, expand=True)

    def choose_folder():
        folder = filedialog.askdirectory()
        if folder:
            preset_var.set(folder)
            save_config(folder_path=folder)

    tk.Button(settings_window, text="Browse...", command=choose_folder).pack(pady=5)
    tk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=5)
    tk.Label(settings_window, bg=bg_color).pack()
    tk.Label(settings_window, bg=bg_color).pack()
    tk.Button(settings_window, text="Clear cache", bg="white", fg="black", command=lambda: clean_cache(wallpaperapplyfolder)).pack()
    tk.Label(settings_window, text="Clear the temporary directory of any image remains from previous folder.", bg=bg_color, fg="white", wraplength=600).pack()
    tk.Button(settings_window, text="Change Background Color", command=change_bg_color, bg="white", fg="black").pack(pady=10)
    tk.Label(settings_window, bg=bg_color, text="Toggle taskbar", fg="white").pack()
    tk.Label(settings_window, bg=bg_color, text="Enjoy the clean view without taskbar in the view! (Reverts back if closed hidden)", fg="white").pack()
    tk.Button(settings_window, text="Show", bg="white", fg="black", command=lambda:taskbarmanager.toggle_taskbars(show=True)).pack()
    tk.Button(settings_window, text="Hide", bg="white", fg="black", command=lambda:taskbarmanager.toggle_taskbars(show=False)).pack(padx=50, pady=10)
    tk.Label(settings_window, bg=bg_color,).pack()
    tk.Label(settings_window, text="(C) 2025 loudtrexx & Herrafoxi under MIT license", bg=bg_color, fg="white").pack()
    tk.Button(settings_window, text="Open project github", bg="white", fg="black", command=lambda: webbrowser.open("https://github.com/loudtrexx/Katieview")).pack()

# --- UI Setup ---
root = tk.Tk()
root.title("Katieview")
root.configure(bg=bg_color)
icon = tk.PhotoImage(file="Assets\\icon.png")
root.iconphoto(False, icon)

folder_var = tk.StringVar(value=f'Folder: "{saved_folder}"' if saved_folder and os.path.isdir(saved_folder) else 'Folder: ')
folder_frame = tk.Frame(root, bg=bg_color)
folder_frame.pack(pady=10)
change_btn = tk.Button(folder_frame, text="Change folder", command=change_folder)
change_btn.grid(row=0, column=0, padx=5)
folder_entry = tk.Entry(folder_frame, textvariable=folder_var, width=50, bg="white", fg="black")
folder_entry.grid(row=0, column=1)

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
thumb_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

if saved_folder and os.path.isdir(saved_folder):
    load_thumbnails(saved_folder)

interval_frame = tk.Frame(root, bg=bg_color)
interval_frame.pack(pady=10)
tk.Label(interval_frame, text="Change wallpaper every...", fg="white", bg=bg_color).pack()
interval_var = tk.IntVar(value=30)
options_frame = tk.Frame(interval_frame, bg=bg_color)
options_frame.pack()
radio_buttons = []
for val in [30, 60, 90]:
    radio = tk.Radiobutton(options_frame, text=str(val), variable=interval_var, value=val, fg="white", bg=bg_color, selectcolor=bg_color)
    radio.pack(side=tk.LEFT, padx=10)
    radio_buttons.append(radio)

custom_var = tk.StringVar()
def validate_number(P): return P.isdigit() or P == ""
vcmd = (root.register(validate_number), '%P')
def select_custom():
    if custom_var.get().isdigit():
        interval_var.set(int(custom_var.get()))
    else:
        interval_var.set(0)

custom_frame = tk.Frame(interval_frame, bg=bg_color)
custom_frame.pack(pady=5)
custom_radio = tk.Radiobutton(custom_frame, text="", variable=interval_var, value=0, fg="white", bg=bg_color, selectcolor=bg_color, command=select_custom)
custom_radio.pack(side=tk.LEFT)
tk.Label(custom_frame, text="Custom (min):", fg="white", bg=bg_color).pack(side=tk.LEFT)
custom_entry = tk.Entry(custom_frame, textvariable=custom_var, width=5, validate="key", validatecommand=vcmd, bg="white", fg="black")
custom_entry.pack(side=tk.LEFT)
custom_entry.bind("<FocusOut>", lambda e: select_custom())
tk.Label(custom_frame, text="minutes.", fg="white", bg=bg_color).pack(side=tk.LEFT, padx=5)

btn_frame = tk.Frame(root, bg=bg_color)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Apply", width=20, command=start_timer).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="Settings...", width=20, command=open_settings).pack(side=tk.LEFT, padx=10)

try:
    os.makedirs(wallpaperapplyfolder, exist_ok=True)
except Exception:
    pass

# Apply color to widgets on load
apply_background_color(bg_color)

root.mainloop()
taskbarmanager.toggle_taskbars(show=True)