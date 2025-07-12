from flask import Flask, send_file, render_template, Response, abort
import threading
import time
import socket
import os
import io
import zipfile

app = Flask(__name__)
file_path = None  # str (file or zip) or list of files

active_download = threading.Event()
download_active = threading.Event()

def format_size(bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.1f} TB"

@app.route("/")
def index():
    if isinstance(file_path, str):
        size_bytes = os.path.getsize(file_path)
        return render_template("download.html", file_name=os.path.basename(file_path), file_size=format_size(size_bytes), is_multiple=False)
    elif isinstance(file_path, list):
        total_size = sum(os.path.getsize(f) for f in file_path)
        return render_template("download.html", file_name="Multiple files", file_size=format_size(total_size), is_multiple=True)
    else:
        return "No files to serve", 404

@app.route("/download")
def download():
    active_download.set()
    download_active.set()

    if isinstance(file_path, str):
        # ✅ Serve static file or zip
        def generate():
            with open(file_path, "rb") as f:
                while chunk := f.read(4096):
                    yield chunk
            download_active.clear()
            # ✅ Delete static zip after send
            if file_path.endswith("shared.zip"):
                os.remove(file_path)

        return Response(
            generate(),
            mimetype="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"}
        )

    elif isinstance(file_path, list):
        # ✅ Zip in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for f in file_path:
                zipf.write(f, arcname=os.path.basename(f))
        zip_buffer.seek(0)

        def generate():
            yield from zip_buffer
            download_active.clear()

        return Response(
            generate(),
            mimetype="application/zip",
            headers={"Content-Disposition": "attachment; filename=shared_files.zip"}
        )

    else:
        return abort(400)

@app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join("static", "favicon.ico"))

def favicon():
    return "", 204

def is_downloading():
    return download_active.is_set()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def start_server_with_timer(path):
    global file_path
    file_path = path
    ip = get_local_ip()

    def run():
        app.run(host="0.0.0.0", port=5000)

    def timer():
        time.sleep(600)
        if not active_download.is_set():
            os._exit(0)

    threading.Thread(target=run).start()
    threading.Thread(target=timer, daemon=True).start()
    return f"http://{ip}:5000"
