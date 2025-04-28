import ctypes
import tkinter

def toggle_taskbars(show=True):
    # Constants for ShowWindow
    SW_SHOW = 5
    SW_HIDE = 0

    # Find the primary taskbar
    hwnd_taskbar = ctypes.windll.user32.FindWindowW("Shell_TrayWnd", None)
    if hwnd_taskbar:
        # Show or hide the primary taskbar
        ctypes.windll.user32.ShowWindow(hwnd_taskbar, SW_SHOW if show else SW_HIDE)

    # Find any secondary taskbars (e.g., on additional monitors)
    hwnd_secondary = ctypes.windll.user32.FindWindowW("Shell_SecondaryTrayWnd", None)
    while hwnd_secondary:
        # Show or hide the secondary taskbar
        ctypes.windll.user32.ShowWindow(hwnd_secondary, SW_SHOW if show else SW_HIDE)

        # Find the next secondary taskbar (if it exists)
        hwnd_secondary = ctypes.windll.user32.FindWindowExW(None, hwnd_secondary, "Shell_SecondaryTrayWnd", None)

    print("Taskbars have been toggled.")

# Example usage
#toggle_taskbars(show=False)  # Hides taskbars on all screens
#toggle_taskbars(show=True)   # Shows taskbars on all screens
