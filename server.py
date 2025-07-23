from flask import Flask, send_file, render_template, Response, abort
import threading
import time
import socket
import os
from dataclasses import dataclass

app = Flask(__name__)
file_path = None  # Always a str path to a file or zip

@dataclass
class DownloadStatus:
    active: bool = False
    result: str = None  # "complete" or "cancelled"
    bytes_sent: int = 0
    total_size: int = 0

download_status = DownloadStatus()

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
        return render_template(
            "download.html",
            file_name=os.path.basename(file_path),
            file_size=format_size(size_bytes),
            is_multiple=False
        )
    return "No files to serve", 404

@app.route("/download")
def download():
    download_status.active = True
    download_status.result = None
    download_status.bytes_sent = 0
    download_status.total_size = 0

    if isinstance(file_path, str):
        file_size = os.path.getsize(file_path)
        download_status.total_size = file_size

        def generate():
            try:
                with open(file_path, "rb") as f:
                    while chunk := f.read(4096):
                        download_status.bytes_sent += len(chunk)
                        yield chunk
                if download_status.bytes_sent == download_status.total_size:
                    download_status.result = "complete"
                else:
                    download_status.result = "cancelled"
            except (ConnectionResetError, GeneratorExit, BrokenPipeError):
                download_status.result = "cancelled"
            finally:
                download_status.active = False

        return Response(
            generate(),
            mimetype="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename={os.path.basename(file_path)}",
                "Content-Length": str(file_size)
            }
        )

    return abort(400)

@app.route('/favicon.ico')
def favicon():
    return send_file(os.path.join("static", "favicon.ico"))

def is_downloading():
    return download_status.active

def get_download_result():
    return download_status.result

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
        if not download_status.active:
            os._exit(0)

    threading.Thread(target=run).start()
    threading.Thread(target=timer, daemon=True).start()
    return f"http://{ip}:5000"
