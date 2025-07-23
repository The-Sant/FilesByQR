from flask import Flask, request, send_from_directory, render_template, abort, jsonify
import tempfile
import os
import socket
import threading
import shutil
import logging

app = Flask(__name__)
upload_dir = tempfile.mkdtemp()
uploaded_files = []
upload_ready = threading.Event()
upload_in_progress = threading.Event()  # 👈 New flag

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload():
    global uploaded_files
    uploaded_files.clear()
    shutil.rmtree(upload_dir, ignore_errors=True)
    os.makedirs(upload_dir, exist_ok=True)

    files = request.files.getlist("file")
    if not files or files[0].filename == '':
        return "No files selected", 400

    upload_in_progress.set()  # 👈 Start uploading
    try:
        for file in files:
            filename = file.filename
            save_path = os.path.join(upload_dir, filename)
            file.save(save_path)
            uploaded_files.append({
                "name": filename,
                "size": os.path.getsize(save_path)
            })
        upload_ready.set()  # 👈 Upload complete
    finally:
        upload_in_progress.clear()  # 👈 Always clear even on error

    return "Upload complete. You can now close this page."

@app.route("/download_uploaded/<filename>")
def download_uploaded(filename):
    if not upload_ready.is_set():
        return abort(404)
    file_path = os.path.join(upload_dir, filename)
    if not os.path.exists(file_path):
        return abort(404)
    return send_from_directory(upload_dir, filename, as_attachment=True)

class NoStatusLogFilter(logging.Filter):
    def filter(self, record):
        return "/status" not in record.getMessage()

log = logging.getLogger('werkzeug')
log.addFilter(NoStatusLogFilter())

@app.route("/status")
def status():
    return jsonify({
        "ready": upload_ready.is_set(),
        "uploading": upload_in_progress.is_set(),  # 👈 Add new key
        "files": uploaded_files if upload_ready.is_set() else []
    })

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

def start_receive_server():
    ip = get_local_ip()

    def run():
        app.run(host="0.0.0.0", port=5001)

    threading.Thread(target=run, daemon=True).start()
    return f"http://{ip}:5001"
