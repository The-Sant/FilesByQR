FilesByQR v1.2 - Instant File Sharing via QR Code  
Created by: Santanu Mondal  

Overview:
-----------
FilesByQR is a lightweight Windows utility that lets you instantly share or receive files over your local network using QR codes.  
You can:
• Right-click any file(s) and select **"Share with QR"** to share instantly  
• Open the app directly to access additional options like **"Send Files"** and **"Receive Files"**  
• Use your phone to upload files to your PC — all through a secure local connection  

Features:
----------
- ✅ Context menu integration: "Share with QR"
- ✅ Lightning-fast local sharing:
    • Single file → shared directly  
    • Multiple files → zipped automatically for easy download  
- ✅ Dual-mode launcher when opened directly:
    • **Send Files**: Select files and share via QR  
    • **Receive Files**: Let other devices upload files directly to your PC  
- ✅ Built-in QR code display and temporary web server
- ✅ Clean, responsive UI with zipping progress and status
- ✅ Local-only sharing — no internet required
- ✅ Automatic cleanup of temporary ZIPs after use
- ✅ Supports long filenames, spaces, and Unicode characters
- ✅ QR auto-expires after countdown for security

Installation:
--------------
1. Run `FilesByQRInstaller.exe`.
2. App installs to **Program Files** and integrates with the right-click menu.
3. On first use, allow LAN access in firewall prompt (required for sharing).
4. Right-click any file or group of files → **Share with QR**

Uninstallation:
----------------
Use the Start Menu or Windows "Apps & Features" to uninstall.  
All registry entries, context menu items, and temporary data will be removed.

System Requirements:
---------------------
- Windows 10 or 11 (64-bit)
- No Python required — packaged as standalone EXE
- Works across any device connected to the same Wi-Fi or LAN

Notes:
-------
- Ensure firewall or antivirus is not blocking local access on port 5000.
- This app uses a temporary local Flask server — data never leaves your network.
- Works best when mobile and PC are on the same subnet (Wi-Fi/router).

Support:
----------
For issues, feedback, or improvements, please contact the developer:  
**Santanu Mondal**
