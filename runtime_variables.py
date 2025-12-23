import os
import sys

BASE_PATH = None

# --- Step 1: Add project subfolders to Python path ---
try:
    BASE_PATH = sys._MEIPASS  # When running as PyInstaller EXE
except Exception:
    BASE_PATH = os.path.abspath(".")