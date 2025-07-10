; -----------------------------
; FilesByQR Inno Setup Script
; Compatible with PyInstaller --onedir
; -----------------------------

[Setup]
AppName=Files By QR
AppVersion=1.0
DefaultDirName={autopf}\Files By QR
DefaultGroupName=Files By QR
OutputDir=dist_installer
OutputBaseFilename=FilesByQRInstaller
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\FilesByQR.exe

[Files]
; ✅ Include all files and folders from the --onedir build output
Source: "dist\FilesByQR\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; ✅ Start Menu shortcut
Name: "{group}\FilesByQR"; Filename: "{app}\FilesByQR.exe"

; ✅ Desktop shortcut
Name: "{commondesktop}\FilesByQR"; Filename: "{app}\FilesByQR.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: checkedonce

[Registry]
; ✅ Right-click context menu: "Share with QR"
Root: HKCR; Subkey: "AllFilesystemObjects\shell\FilesByQR"; ValueType: string; ValueName: ""; ValueData: "Share with QR"; Flags: uninsdeletekey
Root: HKCR; Subkey: "AllFilesystemObjects\shell\FilesByQR"; ValueType: string; ValueName: "Icon"; ValueData: "{app}\assets\app_icon.ico"; Flags: uninsdeletevalue
Root: HKCR; Subkey: "AllFilesystemObjects\shell\FilesByQR\command"; ValueType: string; ValueName: ""; ValueData: """{app}\FilesByQR.exe"" ""%1"""

; ✅ Start with Windows (autorun)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; \
ValueType: string; ValueName: "FilesByQR"; ValueData: """{app}\FilesByQR.exe"""; Flags: uninsdeletevalue

[Run]
; ✅ Launch after install
Filename: "{app}\FilesByQR.exe"; Description: "Launch FilesByQR"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; ✅ Delete app data files (settings, logs)
Type: files; Name: "{userappdata}\FilesByQR\qrshare_log.txt"
Type: files; Name: "{userappdata}\FilesByQR\settings.json"
Type: dirifempty; Name: "{userappdata}\FilesByQR"

; ✅ Delete shared temp file
Type: files; Name: "{tmp}\shared.zip"
Type: dirifempty; Name: "{tmp}\FilesByQR"
