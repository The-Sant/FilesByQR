# startup_manager.py
import winreg as reg
import os

APP_NAME = "FilesByQR"
SCRIPT_PATH = os.path.abspath("main.py")

def add_to_startup():
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                          r"Software\Microsoft\Windows\CurrentVersion\Run",
                          0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key, APP_NAME, 0, reg.REG_SZ, f'"{SCRIPT_PATH}"')
        reg.CloseKey(key)
        print("✔️ Added to startup.")
    except Exception as e:
        print(f"❌ Failed to add to startup: {e}")

def remove_from_startup():
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                          r"Software\Microsoft\Windows\CurrentVersion\Run",
                          0, reg.KEY_SET_VALUE)
        reg.DeleteValue(key, APP_NAME)
        reg.CloseKey(key)
        print("✔️ Removed from startup.")
    except FileNotFoundError:
        print("ℹ️ No startup entry found.")
    except Exception as e:
        print(f"❌ Failed to remove from startup: {e}")

def is_registered():
    try:
        key = reg.OpenKey(reg.HKEY_CURRENT_USER,
                          r"Software\Microsoft\Windows\CurrentVersion\Run",
                          0, reg.KEY_READ)
        value, _ = reg.QueryValueEx(key, APP_NAME)
        reg.CloseKey(key)
        return value.strip('"') == SCRIPT_PATH
    except Exception:
        return False
