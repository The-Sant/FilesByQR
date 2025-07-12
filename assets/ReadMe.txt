readme_content = """
FilesByQR - Instant File Sharing via QR Code

Overview:
-----------
FilesByQR is a lightweight Windows utility that lets you share files and folders over a local network by generating a QR code. Simply right-click any file, choose "Share with QR", and scan the code from your phone or another device on the same Wi-Fi/LAN to download the file instantly.

Features:
----------
- Right-click integration: "Share with QR" in context menu
- Automatic local server with QR generation
- Supports files and folders (with optional zipping)
- Password protection and auto-expiry (optional)
- Drag-and-drop support when opened manually
- Clean uninstall: removes all temp files and registry entries
- No internet required — works fully offline in LAN

Installation:
--------------
1. Run FilesByQRInstaller.exe
2. The app installs to Program Files and adds context menu integration.
3. If prompted, allow network access (especially for private or local networks) when launching the app. No internet access is required or used.
4. After installation, right-click any file/folder → Share with QR

**Note: To allow file sharing over your local network, please ensure that FilesByQR.exe is allowed through your firewall or antivirus.
This app runs a secure local server on your device and may be blocked by some security software by default.**

Uninstallation:
----------------
Use the Windows "Apps & Features" page or Start Menu shortcut to uninstall.
All registry entries and app data will be automatically removed.

System Requirements:
---------------------
- Windows 10 or 11 (64-bit)
- Python is not required after installation (built as EXE)
- Works best on devices connected to the same LAN/Wi-Fi

Created by: Santanu Mondal
"""

with open("/mnt/data/readme.txt", "w", encoding="utf-8") as f:
    f.write(readme_content.strip())

"/mnt/data/readme.txt"
