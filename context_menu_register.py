import winreg as reg
import os

def add_context_menu():
    key_path = r"*\shell\FilesByQR"
    exe_path = os.path.join(os.getcwd(), "FilesByQR.exe")
    icon_path = os.path.join(os.getcwd(), "assets", "app_icon.ico").replace("\\", "\\\\")
    command = f'"{exe_path}" "%1"'

    try:
        # Main key
        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, key_path)
        reg.SetValue(key, '', reg.REG_SZ, 'Share with QR')
        reg.SetValueEx(key, 'Icon', 0, reg.REG_SZ, icon_path)

        # Command subkey
        cmd_key = reg.CreateKey(key, "command")
        reg.SetValue(cmd_key, '', reg.REG_SZ, command)

        print("✅ Context menu entry added.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    add_context_menu()
