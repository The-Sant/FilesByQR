import zipfile, os

def zip_files_if_needed(files):
    if len(files) == 1:
        return files[0], False  # ✅ Single file

    total_size = sum(os.path.getsize(f) for f in files)

    if total_size >= 2 * 1024 * 1024 * 1024:  # 2 GB
        # ✅ Zip to disk
        zip_path = "temp/shared.zip"
        os.makedirs("temp", exist_ok=True)

        if os.path.exists(zip_path):
            os.remove(zip_path)

        with zipfile.ZipFile(zip_path, 'w') as zf:
            for file in files:
                zf.write(file, arcname=os.path.basename(file))

        return zip_path, True  # return static zip

    else:
        return list(files), False  # ✅ return as list for in-memory zip
