import zipfile
import os
import sys
import random
from datetime import datetime
import tempfile

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def zip_files_if_needed(files, progress_callback=None):
    if len(files) == 1:
        return files[0], False

    temp_dir = os.path.join(tempfile.gettempdir(), "FilesByQR")
    os.makedirs(temp_dir, exist_ok=True)

    short_time = datetime.now().strftime("%H%M")
    suffix = random.randint(10, 99)
    zip_name = f"shared_{short_time}_{suffix}.zip"
    zip_path = os.path.join(temp_dir, zip_name)

    with zipfile.ZipFile(zip_path, 'w') as zf:
        total = len(files)
        for i, file in enumerate(files, start=1):
            zf.write(file, arcname=os.path.basename(file))
            if progress_callback:
                progress_callback(i, total, file)

    return zip_path, True
