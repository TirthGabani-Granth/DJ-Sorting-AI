import os
from pathlib import Path

# --- External APIs (Optional) ---
# JIOSAAVN_BASE_URL = "https://saavn.me" # Disable for faster initial run
LASTFM_API_KEY = ""
ACOUSTID_API_KEY = ""

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FOLDER = r"e:\ALL PROJECTS\Dj AI automation\Song"
OUTPUT_FOLDER = str(BASE_DIR / "sorted song")
DATABASE_PATH = str(BASE_DIR / "database" / "songs_v4.db")

# --- Confidence Thresholds ---
CONFIDENCE_L1 = 0.80   # Layer 1 stops if score >= this
CONFIDENCE_L2 = 0.70   # Layer 2 stops if score >= this

# --- Audio Segment Settings ---
AUDIO_START_SEC = 25     # Skip first 25 seconds of every song
AUDIO_DURATION_L2 = 30     # Whisper uses 30 seconds (25s to 55s)
AUDIO_DURATION_L3 = 60     # librosa uses 60 seconds (25s to 85s)

# --- Processing ---
BATCH_SIZE = 50     # Process 50 songs at a time

# Ensure output and DB folders exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
