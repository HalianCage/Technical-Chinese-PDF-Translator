import threading
import uvicorn
import sys
import os
import subprocess
import uuid
import requests
import json
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from cryptography.fernet import Fernet


# --- Load environment variables ---
load_dotenv()



# --- Step 1: Add project subfolders to Python path ---
try:
    base_path = sys._MEIPASS  # When running as PyInstaller EXE
except Exception:
    base_path = os.path.abspath(".")

sys.path.append(os.path.join(base_path, 'frontend'))
sys.path.append(os.path.join(base_path, 'backend'))



# --- Constants ---
ACTIVATION_SERVER_URL = "https://chinese-cad-activation-server.vercel.app/api/activate"  # <--- CHANGE THIS
APP_NAME = "Chinese-CAD-Translation"
LICENSE_FILE_DIR = os.path.join(os.environ['APPDATA'], APP_NAME)
LICENSE_FILE_PATH = os.path.join(LICENSE_FILE_DIR, 'license.dat')
# 🛑 SECURITY NOTE: 
# In a Python app, strings can be found by hackers. 
# For maximum security, use PyArmor to obfuscate this script.
# This MUST match the key in your admin_keygen.py
SECRET_KEY = b'2avw6AEzFpQO-Zt-a0gxSndOcwRJC5QobzJzijHFW1o='



# --- Import app components ---
try:
    from backend.main import logger

    logger.info("Trying to import from backend")
    # Import the FastAPI 'app' object from your backend
    # !! IMPORTANT: I am assuming your file is 'backend/main.py' 
    # !! and your FastAPI object is named 'app'. 
    # !! If not, change 'main' or 'app' to match your code.
    from backend.main import app as backend_app
    from frontend.gui import App as FrontendApp
except ImportError as e:
    logger.error(f"Error: Failed to import modules. {e}")
    logger.error("Please ensure:")
    logger.error("1. This script is in your root project folder.")
    logger.error("2. You have a 'frontend/main_gui.py' file with your 'App' class.")
    logger.error("3. You have a 'backend/main.py' file (or similar) with your FastAPI 'app'.")
    logger.error("Press Enter to exit...")
    sys.exit(1)



''' --- License Activation Flow --- '''
def activate_or_validate_license():
    os.makedirs(LICENSE_FILE_DIR, exist_ok=True)
    current_hwid = get_my_hardware_id()

    # 1️⃣ Check if we already have a valid license
    if validate_license_file(current_hwid):
        logger.info("License valid. Launching app.")
        run_main_application()
        return

    # 2️⃣ No valid license? Show the "Offline Activation" Window
    show_activation_dialog(current_hwid)


# License activation UI
def show_activation_dialog(current_hwid):
    """
    Displays a window forcing the user to enter a license key.
    """
    root = tk.Tk()
    root.title("Activation Required")
    root.geometry("500x300")
    
    # Label: Instructions
    lbl_info = tk.Label(root, text="This application is not activated.", font=("Arial", 12, "bold"))
    lbl_info.pack(pady=10)

    lbl_instr = tk.Label(root, text=f"Please share the below Unique Generated Key to\n\n{current_hwid}", font=("Arial", 10))
    lbl_instr.pack(pady=10)
    
    # Input: License Key Paste Area
    lbl_key = tk.Label(root, text="And paste your received License Activation Key below:")
    lbl_key.pack()
    
    entry_key = tk.Entry(root, width=50)
    entry_key.pack(pady=5)

    def on_activate():
        # Get the key the user pasted
        key_input = entry_key.get().strip()
        
        # Save it to the license file
        try:
            # User might paste the string, we need bytes
            with open(LICENSE_FILE_PATH, 'wb') as f:
                f.write(key_input.encode())
            
            # Check if it works
            if validate_license_file(current_hwid):
                messagebox.showinfo("Success", "Activation Successful! Please restart the app.")
                root.destroy()
                sys.exit(0) # Exit so they restart fresh
            else:
                messagebox.showerror("Error", "Invalid License Key.\nMake sure you pasted the entire string.")
                # We don't close the window, let them try again
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save license: {e}")

    btn_activate = tk.Button(root, text="Activate License", command=on_activate, bg="#4CAF50", fg="white")
    btn_activate.pack(pady=20)

    # Handle Window Close (Exit App)
    def on_close():
        root.destroy()
        sys.exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


# --- Licensing Helper Functions ---
def get_my_hardware_id():
    """
    Generate a unique, stable HWID using Machine UUID.
    """
    try:
        uuid = subprocess.check_output(
            ['powershell', '-Command',
            'Get-CimInstance Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID'],
            text=True
        ).strip()


        logger.info(f"uuid: {uuid}")

        return uuid

    except Exception as e:
        logger.error(f"Error retrieving UUID: {e}")
        return None


def validate_license_file(hwid):
    """
    Reads the license file and tries to decrypt it.
    If it decrypts successfully AND matches the HWID, it is valid.
    """
    if not os.path.exists(LICENSE_FILE_PATH):
        return False

    try:
        with open(LICENSE_FILE_PATH, 'rb') as f:
            encrypted_token = f.read()

        cipher_suite = Fernet(SECRET_KEY)
        decrypted_hwid = cipher_suite.decrypt(encrypted_token).decode()

        if decrypted_hwid == hwid:
            return True
    except Exception as e:
        logger.error(f"License validation failed: {e}")
    
    return False

def show_error_popup(title, message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, message)
    root.destroy()
    sys.exit(1)

# --- Start Backend (Uvicorn) ---
def start_backend():
    logger.info("Starting backend server on separate thread...")
    try:
        uvicorn.run(
            backend_app,
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_config=None
        )
    except Exception as e:
        logger.error(f"Backend server failed: {e}")

# --- Main app launcher ---
def run_main_application():
    logger.info("Launching main application...")

    # 4a. Start the backend server in a background thread
    # We use daemon=True so it automatically shuts down
    # when the main GUI app is closed.
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    # 4b. Start the frontend GUI on the main thread
    # This is a blocking call. The script will stay here
    # until the user closes the CustomTkinter window.
    logger.info("Starting frontend GUI on main thread...")
    gui = FrontendApp()
    gui.mainloop()

    # 4c. (Implicit)
    # When the GUI window is closed, mainloop() exits.
    # The script ends. The daemon backend thread is killed.
    logger.info("Frontend closed. Exiting app.")

# --- Entry Point ---
if __name__ == "__main__":
    activate_or_validate_license()
