import threading
import uvicorn
import sys
import os
import uuid
import requests
import json
import tkinter
from tkinter import messagebox
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Step 1: Add project subfolders to Python path ---
try:
    base_path = sys._MEIPASS  # When running as PyInstaller EXE
except Exception:
    base_path = os.path.abspath(".")

sys.path.append(os.path.join(base_path, 'frontend'))
sys.path.append(os.path.join(base_path, 'backend'))

# --- Constants ---``
ACTIVATION_SERVER_URL = "https://chinese-cad-activation-server.vercel.app/api/activate"  # <--- CHANGE THIS
APP_NAME = "Chinese-CAD-Translation"

LICENSE_FILE_DIR = os.path.join(os.environ['APPDATA'], APP_NAME)
LICENSE_FILE_PATH = os.path.join(LICENSE_FILE_DIR, 'license.dat')

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

# --- Licensing Helper Functions ---
def get_my_hardware_id():
    """
    Generate a unique, stable HWID using MAC + Machine UUID.
    """
    try:
        mac = uuid.getnode()
        sys_id = uuid.uuid1().int >> 64  # Add system randomness
        return str(abs(hash((mac, sys_id))))  # Hash for privacy
    except Exception as e:
        print(f"[ERROR] Could not generate HWID: {e}")
        show_error_popup("License Error", "Failed to generate device ID.")
        sys.exit(1)

def show_error_popup(title, message):
    root = tkinter.Tk()
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

# --- License Activation Flow ---
def activate_or_validate_license():
    os.makedirs(LICENSE_FILE_DIR, exist_ok=True)

    current_hwid = get_my_hardware_id()
    saved_hwid = None

    # 1️⃣ Check local license
    if os.path.exists(LICENSE_FILE_PATH):
        try:
            with open(LICENSE_FILE_PATH, 'r') as f:
                saved_hwid = f.read().strip()
        except Exception as e:
            show_error_popup("License Error", f"Could not read license file: {e}")

    # 2️⃣ Fast Path: Local validation
    if current_hwid == saved_hwid:
        logger.info("License validated locally.")
        run_main_application()
        sys.exit(0)

    # 3️⃣ Slow Path: Online activation
    logger.info("No valid local license. Activating online...")

    root = tkinter.Tk()
    root.title("Activating")
    root.geometry("250x50")
    label = tkinter.Label(root, text="Activating, please wait...")
    label.pack(pady=10, padx=10)
    root.update()

    try:
        response = requests.post(
            ACTIVATION_SERVER_URL,
            json={'hwid': current_hwid},
            timeout=15
        )
        data = response.json()

        if response.status_code == 200 and data['status'] == 'success':
            logger.info("Activation successful. Saving license locally.")
            with open(LICENSE_FILE_PATH, 'w') as f:
                f.write(current_hwid)

            root.destroy()
            run_main_application()
        else:
            root.destroy()
            show_error_popup("Activation Failed", f"Error: {data.get('message', 'Unknown error')}")
    except Exception as e:
        root.destroy()
        show_error_popup("Connection Error", f"Could not connect to activation server.\n\n({e})")

# --- Entry Point ---
if __name__ == "__main__":
    activate_or_validate_license()
