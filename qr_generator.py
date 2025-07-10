import qrcode
import tkinter as tk
from PIL import Image, ImageTk
import tempfile
import os
import server  # to check download status

def generate_qr(url, file_name=None):
    # Generate QR code and save to temp file
    qr_img = qrcode.make(url)
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    qr_img.save(temp_path)

    # Base root (invisible)
    root = tk.Tk()
    root.withdraw()

    # QR popup window
    popup = tk.Toplevel(root)
    popup.title("Files by QR")
    popup.geometry("280x420")
    popup.resizable(False, False)

    # ✅ Center window after it's created
    root.eval('tk::PlaceWindow %s center' % popup.winfo_pathname(popup.winfo_id()))

    # QR Image
    img = Image.open(temp_path)
    img = img.resize((240, 240), Image.Resampling.LANCZOS)
    img_tk = ImageTk.PhotoImage(img, master=popup)

    qr_label = tk.Label(popup, image=img_tk)
    qr_label.image = img_tk
    qr_label.pack(pady=(30, 5))

    # Optional file name
    if file_name:
        # Truncate if longer than 30 characters
        display_name = file_name if len(file_name) <= 30 else file_name[:27] + "..."

        name_label = tk.Label(
            popup,
            text=display_name,
            font=("Arial", 9),
            wraplength=240,
            justify="center"
        )
        name_label.pack(pady=(5, 5))

        # Tooltip with full file name
        def show_tooltip(event):
            tooltip = tk.Toplevel(popup)
            tooltip.wm_overrideredirect(True)
            tooltip.geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(
                tooltip,
                text=file_name,
                font=("Arial", 9),
                bg="lightyellow",
                relief="solid",
                bd=1
            )
            label.pack()
            name_label.tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(name_label, 'tooltip'):
                name_label.tooltip.destroy()
                del name_label.tooltip

        name_label.bind("<Enter>", show_tooltip)
        name_label.bind("<Leave>", hide_tooltip)


    # Timer + Downloading status
    status_frame = tk.Frame(popup)
    status_frame.pack(pady=(5, 5))

    timer_var = tk.StringVar(master=root)
    timer_var.set("Expires in 10:00")

    timer_label = tk.Label(
        status_frame,
        textvariable=timer_var,
        font=("Arial", 10, "bold"),
        fg="#4B0C0C"
    )

    downloading_label = tk.Label(
        status_frame,
        text="Downloading...",
        font=("Arial", 10, "bold"),
        fg="green"
    )

    timer_label.pack()


    time_left = 600
    download_was_active = False

    def update_timer():
        nonlocal time_left, download_was_active

        if hasattr(server, 'is_downloading') and server.is_downloading():
            if not download_was_active:
                timer_label.pack_forget()
                downloading_label.pack()
                download_was_active = True
        else:
            if download_was_active:
                downloading_label.pack_forget()
                timer_label.pack()
                download_was_active = False

            if time_left <= 0:
                root.destroy()
                os._exit(0)

            mins, secs = divmod(time_left, 60)
            timer_var.set(f"Expires in {mins:02}:{secs:02}")
            time_left -= 1

        popup.after(1000, update_timer)

    def on_finish():
        root.destroy()
        os._exit(0)

    finish_btn = tk.Button(
        popup,
        text="Finish",
        command=on_finish,
        font=("Arial", 10, "bold"),
        bg="#2563eb",         # background color (blue)
        fg="white",           # text color
        activebackground="#0e2972",  # on click
        activeforeground="white",
        relief="raised",      # button 3D style
        bd=1,                 # border width
        cursor="hand2"        # cursor on hover
    )
    finish_btn.pack(pady=(10, 10), ipadx=10, ipady=4)


    # Start timer loop
    update_timer()

    # Topmost for better visibility
    popup.attributes('-topmost', True)
    popup.after(100, lambda: popup.attributes('-topmost', False))

    root.mainloop()
