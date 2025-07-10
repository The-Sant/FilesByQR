import winreg as reg
import os

def add_context_menu():
    key_path = r"*\shell\FilesByQR"
    command = rf'"{os.getcwd()}\\main.py" "%1"'

    try:
        key = reg.CreateKey(reg.HKEY_CLASSES_ROOT, key_path)
        reg.SetValue(key, '', reg.REG_SZ, 'Share with QR')
        reg.SetValueEx(key, 'Icon', 0, reg.REG_SZ, os.path.join(os.getcwd(), 'assets\\app_icon.ico'))

        cmd_key = reg.CreateKey(key, "command")
        reg.SetValue(cmd_key, '', reg.REG_SZ, command)
        print("Context menu entry added.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    add_context_menu()
