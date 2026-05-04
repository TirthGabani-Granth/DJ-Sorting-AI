import os
from pathlib import Path
from typing import List

SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma'}

def scan_folder(folder_path: str) -> List[Path]:
    """Scans the given folder for supported audio files."""
    path = Path(folder_path)
    if not path.exists() or not path.is_dir():
        print(f"Error: Folder {folder_path} does not exist.")
        return []
        
    audio_files = []
    
    for ext in SUPPORTED_FORMATS:
        audio_files.extend(path.rglob(f"*{ext}"))
        audio_files.extend(path.rglob(f"*{ext.upper()}"))
        
    # Remove duplicates (rglob might find the same if mixed case somehow, though unlikely with precise globbing)
    audio_files = list(set(audio_files))
    print(f"Found {len(audio_files)} audio files in {folder_path}")
    return audio_files
