import qrcode
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import tempfile
import os
import shutil
import server
from utils import resource_path

class QRWindow:
    def __init__(self, file_name, zip_path=None):
        self.temp_qr_path = None
        self.file_name = file_name
        self.cancelled = False

        self.root = tk.Tk()
        self.root.withdraw()

        self.root.title("Files by QR - Send Files")
        self.root.iconbitmap(resource_path("assets/app_icon.ico"))
        self.root.geometry("280x460")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.after(100, lambda: self.root.attributes("-topmost", False))
        self.root.eval('tk::PlaceWindow %s center' % self.root.winfo_pathname(self.root.winfo_id()))

        self.root.deiconify()

        # ❌ Don't pack these yet — defer until needed
        self.zipping_label = tk.Label(self.root, text="Zipping in progress...\nPlease wait.",
                                    font=("Arial", 10, "bold"), fg="gray")
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=200, mode="determinate")
        self.percentage_label = tk.Label(self.root, text="", font=("Arial", 9))
        self.filename_label = tk.Label(self.root, text="", font=("Arial", 9), wraplength=240, justify="center")

        self.cancel_btn = tk.Button(self.root, text="Cancel", font=("Arial", 10, "bold"),
                                    command=self.cleanup_and_exit, bg="white", fg="red",
                                    relief="raised", cursor="hand2")

        self.qr_label = None
        self.name_label = None
        self.status_frame = None
        self.timer_label = None
        self.downloading_label = None
        self.download_done_label = None
        self.finish_btn = None

        self.root.protocol("WM_DELETE_WINDOW", self.cleanup_and_exit)
        self.zip_path = zip_path

    def show_zipping_ui(self):
        self.zipping_label.pack(pady=(40, 5))
        self.progress.pack(pady=(0, 5))
        self.percentage_label.pack()
        self.filename_label.pack(pady=(5, 5))
        self.cancel_btn.pack(side="bottom", pady=(10, 50), ipadx=10, ipady=4)

    def update_zip_progress(self, current, total, filename):
        self.progress["maximum"] = total
        self.progress["value"] = current
        percent = int((current / total) * 100)
        self.percentage_label.config(text=f"{percent}% complete")
        self.filename_label.config(text=os.path.basename(filename))
        self.root.update_idletasks()

    def update_with_url(self, url):
        self.zipping_label.pack_forget()
        self.progress.pack_forget()
        self.percentage_label.pack_forget()
        self.filename_label.pack_forget()
        self.cancel_btn.pack_forget()

        if self.qr_label:
            self.qr_label.destroy()

        qr_img = qrcode.make(url)
        self.temp_qr_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
        qr_img.save(self.temp_qr_path)

        img = Image.open(self.temp_qr_path).resize((240, 240), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img, master=self.root)

        self.qr_label = tk.Label(self.root, image=img_tk)
        self.qr_label.image = img_tk
        self.qr_label.pack(pady=(30, 5))

        if self.file_name:
            display_name = self.file_name if len(self.file_name) <= 30 else self.file_name[:27] + "..."
            self.name_label = tk.Label(self.root, text=display_name, font=("Arial", 9), wraplength=240, justify="center")
            self.name_label.pack(pady=(5, 5))

            def show_tooltip(event):
                tooltip = tk.Toplevel(self.root)
                tooltip.wm_overrideredirect(True)
                tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
                label = tk.Label(tooltip, text=self.file_name, font=("Arial", 9), bg="lightyellow", relief="solid", bd=1)
                label.pack()
                self.name_label.tooltip = tooltip

            def hide_tooltip(event):
                if hasattr(self.name_label, 'tooltip'):
                    self.name_label.tooltip.destroy()
                    del self.name_label.tooltip

            self.name_label.bind("<Enter>", show_tooltip)
            self.name_label.bind("<Leave>", hide_tooltip)

        self.status_frame = tk.Frame(self.root)
        self.status_frame.pack(pady=(5, 5))

        timer_var = tk.StringVar(master=self.root)
        timer_var.set("Expires in 10:00")

        self.timer_label = tk.Label(self.status_frame, textvariable=timer_var, font=("Arial", 10, "bold"), fg="#4B0C0C")
        self.downloading_label = tk.Label(self.status_frame, text="Downloading...", font=("Arial", 10, "bold"), fg="green")
        self.download_done_label = tk.Label(self.status_frame, text="✔ Download complete", font=("Arial", 10, "bold"), fg="green")

        self.timer_label.pack()

        self.time_left = 600
        self.download_was_active = False

        def update_timer():
            if server.is_downloading():
                if not self.download_was_active:
                    self.timer_label.pack_forget()
                    self.download_done_label.pack_forget()
                    self.downloading_label.pack()
                    self.download_was_active = True
            else:
                if self.download_was_active:
                    self.downloading_label.pack_forget()
                    self.download_done_label.pack()
                    self.root.after(3000, lambda: (
                        self.download_done_label.pack_forget(),
                        self.timer_label.pack()
                    ))
                    self.download_was_active = False

                if self.time_left <= 0:
                    self.cleanup_and_exit()

                mins, secs = divmod(self.time_left, 60)
                timer_var.set(f"Expires in {mins:02}:{secs:02}")
                self.time_left -= 1

            self.root.after(1000, update_timer)

        update_timer()

        self.finish_btn = tk.Button(
            self.root, text="Finish", command=self.cleanup_and_exit,
            font=("Arial", 10, "bold"), bg="#2563eb", fg="white",
            activebackground="#0e2972", activeforeground="white",
            relief="raised", bd=1, cursor="hand2"
        )
        self.finish_btn.pack(pady=(10, 10), ipadx=10, ipady=4)

    def cleanup_and_exit(self):
        self.cancelled = True
        try:
            if self.zip_path and os.path.exists(self.zip_path):
                os.remove(self.zip_path)
            if hasattr(self, 'temp_qr_path') and os.path.exists(self.temp_qr_path):
                os.remove(self.temp_qr_path)
            legacy_zip = os.path.join("temp", "shared_files.zip")
            if os.path.exists(legacy_zip):
                os.remove(legacy_zip)
            if os.path.exists("temp"):
                shutil.rmtree("temp", ignore_errors=True)
        except Exception as e:
            print("Cleanup error:", e)
        try:
            self.root.destroy()
        except Exception:
            pass
        os._exit(0)

    def run(self):
        self.root.mainloop()
