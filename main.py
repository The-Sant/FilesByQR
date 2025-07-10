import sys
import os
from tkinter import filedialog, Tk, messagebox
from server import start_server_with_timer
from qr_generator import generate_qr
from utils import zip_files_if_needed

if __name__ == "__main__":
    # ✅ Ensure it's a list, not tuple
    files = list(sys.argv[1:])

    if not files:
        root = Tk()
        root.withdraw()
        messagebox.showinfo("Files by QR", "No files passed. Please select file(s) manually.")
        files = filedialog.askopenfilenames(title="Select file(s) to share")
        if not files:
            sys.exit()

    # ✅ Correctly unpack return value
    path_to_serve, zipped = zip_files_if_needed(files)

    # ✅ Check file existence
    if isinstance(path_to_serve, list):
        for f in path_to_serve:
            if not os.path.exists(f):
                print(f"Missing file: {f}")
                sys.exit()
    elif not os.path.exists(path_to_serve):
        print(f"Missing file: {path_to_serve}")
        sys.exit()

    # ✅ Start server and generate QR
    url = start_server_with_timer(path_to_serve)
    label = os.path.basename(path_to_serve) if isinstance(path_to_serve, str) else "Multiple files"
    generate_qr(url, label)
