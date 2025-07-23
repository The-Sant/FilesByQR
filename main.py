import sys
import os
import threading
import tkinter as tk
from tkinter import filedialog
from server import start_server_with_timer
from qr_generator import QRWindow
from qr_receive import generate_receive_qr
from utils import zip_files_if_needed, resource_path
import logging

# ✅ Setup logging
log_dir = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "FilesByQR")
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "FilesByQR_log.txt")

logging.basicConfig(
    filename=log_path,
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def show_message_with_options():
    """GUI to choose between Send Files or Receive Files."""
    result = {"mode": None}
    win = tk.Tk()
    win.withdraw()

    win.title("Files by QR")
    win.iconbitmap(resource_path("assets/app_icon.ico"))
    win.configure(bg="#ffffff")
    win.resizable(False, False)
    win.attributes("-topmost", True)

    # Center the window
    win.update_idletasks()
    width, height = 380, 200
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f"{width}x{height}+{x}+{y}")
    win.deiconify()

    # Layout
    container = tk.Frame(win, bg="white", padx=20, pady=20)
    container.pack(fill="both", expand=True)

    tk.Label(
        container,
        text="Select an action to continue",
        font=("Segoe UI", 12, "bold"),
        bg="white",
        fg="#202020"
    ).pack(pady=(0, 20))

    button_frame = tk.Frame(container, bg="white")
    button_frame.pack()

    def on_send_files():
        result["mode"] = "send"
        win.destroy()

    def on_receive_files():
        result["mode"] = "receive"
        win.destroy()

    def on_close():
        win.destroy()
        sys.exit()

    primary_style = {
        "font": ("Segoe UI", 10, "bold"),
        "bg": "#2563eb",
        "fg": "white",
        "activebackground": "#1e4fc5",
        "activeforeground": "white",
        "relief": "flat",
        "bd": 0,
        "width": 14,
        "cursor": "hand2",
        "padx": 8,
        "pady": 6
    }

    tk.Button(button_frame, text="Send Files", command=on_send_files, **primary_style).pack(side="left", padx=10)
    tk.Button(button_frame, text="Receive Files", command=on_receive_files, **primary_style).pack(side="left", padx=10)

    shadow = tk.Frame(container, bg="#d0d0d0")
    shadow.pack(pady=(25, 0))

    tk.Button(
        shadow,
        text="Cancel",
        command=on_close,
        font=("Segoe UI", 9, "bold"),
        bg="white",
        fg="#cc0000",
        activebackground="#fbeaea",
        activeforeground="#cc0000",
        relief="flat",
        cursor="hand2",
        padx=10,
        pady=4
    ).pack(padx=1, pady=1)

    win.protocol("WM_DELETE_WINDOW", on_close)
    win.grab_set()
    win.wait_window()

    return result["mode"]

# ✅ STEP 1: Handle context menu or drag/drop arguments
files = []
if len(sys.argv) > 1:
    logging.debug("🟢 App started with args: %s", sys.argv)
    files = sys.argv[1:]
    files = [f for f in files if os.path.isfile(f)]

    logging.debug("📂 Parsed files: %s", files)

    if not files:
        logging.warning("⚠️ No valid files found in args. Exiting.")
        sys.exit()

    qr_window = QRWindow(None)

    def background_task():
        try:
            if len(files) == 1:
                logging.debug("🟩 Single file - skip zipping: %s", files[0])
                path_to_serve = files[0]
                is_zipped = False
                qr_window.file_name = os.path.basename(path_to_serve)
                qr_window.zip_path = None
            else:
                logging.debug("📦 Multiple files - start zipping")
                qr_window.show_zipping_ui()

                def update_progress(i, total, fname):
                    if qr_window.cancelled:
                        return
                    qr_window.root.after(0, lambda: qr_window.update_zip_progress(i, total, fname))

                path_to_serve, is_zipped = zip_files_if_needed(files, progress_callback=update_progress)
                qr_window.file_name = os.path.basename(path_to_serve)
                qr_window.zip_path = path_to_serve if is_zipped else None

            if qr_window.cancelled:
                logging.info("❌ Cancelled before serving")
                return

            url = start_server_with_timer(path_to_serve)
            logging.info("🌐 Server started at: %s", url)

            if not qr_window.cancelled:
                qr_window.root.after(0, lambda: qr_window.update_with_url(url))

        except Exception as e:
            logging.exception("🛑 Exception in background_task:")

    threading.Thread(target=background_task, daemon=True).start()
    qr_window.run()
    sys.exit()

# ✅ STEP 2: If no args — show GUI
mode = show_message_with_options()

if mode == "receive":
    generate_receive_qr()
    sys.exit()
elif mode != "send":
    sys.exit()

# ✅ STEP 3: GUI — user selects files
files = filedialog.askopenfilenames(title="Files by QR: Select file(s) to share")
if not files:
    sys.exit()

qr_window = QRWindow(None)

def gui_background_task():
    try:
        if len(files) > 1:
            qr_window.show_zipping_ui()

        def update_progress(i, total, fname):
            if qr_window.cancelled:
                return
            qr_window.root.after(0, lambda: qr_window.update_zip_progress(i, total, fname))

        path_to_serve, is_zipped = zip_files_if_needed(files, progress_callback=update_progress)
        if qr_window.cancelled:
            return

        qr_window.file_name = os.path.basename(path_to_serve)
        qr_window.zip_path = path_to_serve if is_zipped else None
        url = start_server_with_timer(path_to_serve)

        if not qr_window.cancelled:
            qr_window.root.after(0, lambda: qr_window.update_with_url(url))

    except Exception as e:
        logging.exception("🛑 GUI Background Task Error:")

threading.Thread(target=gui_background_task, daemon=True).start()
qr_window.run()
