import qrcode
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import tempfile
import os
import requests
import threading
import receive_server
import shutil
from utils import resource_path

def generate_receive_qr():
    url = receive_server.start_receive_server()

    # Generate QR code and save to temp
    qr_img = qrcode.make(url)
    temp_qr_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    qr_img.save(temp_qr_path)

    root = tk.Tk()
    root.withdraw()

    root.title("Files by QR - Receive Files")
    root.iconbitmap(resource_path("assets/app_icon.ico"))
    root.geometry("280x460")
    root.resizable(False, False)

    # Center window
    root.update_idletasks()
    w, h = 280, 460
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.deiconify()

    # QR image
    img = Image.open(temp_qr_path).resize((240, 240), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img, master=root)
    qr_label = tk.Label(root, image=img_tk)
    qr_label.image = img_tk
    qr_label.pack(pady=(30, 5))

    # Info label
    info_var = tk.StringVar(value="Waiting for upload...")
    info_label = tk.Label(root, textvariable=info_var, font=("Arial", 9), fg="gray", wraplength=240, justify="center")
    info_label.pack(pady=(5, 5))

    tooltip = None

    def show_tooltip(event, text):
        nonlocal tooltip
        tooltip = tk.Toplevel(root)
        tooltip.wm_overrideredirect(True)
        tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        label = tk.Label(tooltip, text=text, font=("Arial", 9), bg="lightyellow", relief="solid", bd=1)
        label.pack()

    def hide_tooltip(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None

    def cleanup_temp():
        if os.path.exists(temp_qr_path):
            try:
                os.remove(temp_qr_path)
            except Exception as e:
                print("QR cleanup failed:", e)

        if hasattr(receive_server, 'upload_dir') and os.path.exists(receive_server.upload_dir):
            try:
                shutil.rmtree(receive_server.upload_dir, ignore_errors=True)
            except Exception as e:
                print("Upload dir cleanup failed:", e)

    def close_popup():
        cleanup_temp()
        root.destroy()
        os._exit(0)

    def download_all_files():
        try:
            r = requests.get(url + "/status")
            files = r.json().get("files", [])
            for f in files:
                name = f["name"]
                r = requests.get(f"{url}/download_uploaded/{name}", stream=True)
                if r.status_code == 200:
                    save_path = os.path.join(os.path.expanduser("~"), "Downloads", name)
                    with open(save_path, "wb") as out:
                        shutil.copyfileobj(r.raw, out)

            info_var.set("✅ All files saved to Downloads")
            download_btn.config(state="disabled")

            if messagebox.askyesno("Files by QR", "Download complete.\nOpen Downloads folder?"):
                os.startfile(os.path.join(os.path.expanduser("~"), "Downloads"))

            close_popup()

        except Exception as e:
            info_var.set(f"Error: {e}")

    download_btn = tk.Button(
        root,
        text="Download",
        state="disabled",
        command=download_all_files,
        font=("Arial", 10, "bold"),
        bg="#4383e2",
        fg="white",
        activebackground="#2a5bb6",
        activeforeground="white",
        relief="raised",
        bd=1,
        cursor="hand2"
    )
    download_btn.pack(pady=(10, 5), ipadx=10, ipady=4)

    close_btn = tk.Button(
        root,
        text="Close",
        command=close_popup,
        font=("Arial", 10, "bold"),
        bg="#3a3a3a",
        fg="white",
        activebackground="#303030",
        activeforeground="white",
        relief="raised",
        bd=1,
        cursor="hand2"
    )
    close_btn.pack(pady=(10, 10), ipadx=10, ipady=4)

    root.protocol("WM_DELETE_WINDOW", close_popup)

    # Upload detection state
    upload_detected = [False]

    def poll_upload_status():
        try:
            r = requests.get(url + "/status", timeout=1)
            data = r.json()
            files = data.get("files", [])
            total_size = sum(f["size"] for f in files)

            # Switch from "waiting" to "uploading..."
            if total_size > 0 and not upload_detected[0]:
                upload_detected[0] = True
                info_var.set("Uploading...")
                info_label.config(fg="green", font=("Arial", 10, "bold"))

            if data.get("ready"):
                size_str = f"{total_size / 1024:.1f} KB" if total_size < 1024**2 else f"{total_size / 1024 / 1024:.1f} MB"

                if len(files) == 1:
                    name = files[0]["name"]
                    truncated = name if len(name) <= 30 else name[:27] + "..."
                    info_var.set(f"{truncated}\nFile Size: {size_str}")
                    info_label.bind("<Enter>", lambda e, t=name: show_tooltip(e, t))
                else:
                    info_var.set(f"{len(files)} Files to Download\nTotal Size: {size_str}")
                    tooltip_text = ""
                    for f in files:
                        size = f["size"]
                        s = f"{size / 1024:.1f} KB" if size < 1024**2 else f"{size / 1024 / 1024:.1f} MB"
                        tooltip_text += f"{f['name']} — {s}\n"
                    tooltip_text = tooltip_text.strip()
                    info_label.bind("<Enter>", lambda e, t=tooltip_text: show_tooltip(e, t))

                info_label.bind("<Leave>", hide_tooltip)
                download_btn.config(state="normal")

        except:
            pass

        root.after(1000, poll_upload_status)

    poll_upload_status()

    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))

    root.mainloop()
