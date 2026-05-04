import os
import shutil
from pathlib import Path
from models.song import SongData

def safe_copy(src: str, dest_dir: str):
    """Copies a file to dest_dir, creating dest_dir if it doesn't exist."""
    os.makedirs(dest_dir, exist_ok=True)
    file_name = os.path.basename(src)
    dest_path = os.path.join(dest_dir, file_name)
    
    if not os.path.exists(dest_path):
        try:
            shutil.copy2(src, dest_path)
            return True
        except Exception as e:
            print(f"Error copying {file_name} to {dest_dir}: {e}")
            return False
    return True # Already exists

def copy_song_to_folders(song: SongData, output_base_folder: str):
    """Copies the song to a structured path: Language / Region / Industry / Occasion."""
    if not os.path.exists(song.file_path):
        return False
        
    base = Path(output_base_folder)
    
    # --- STRICT CHECK: IF UNSURE, MOVE TO MISMATCH ---
    confidence = song.calculate_confidence()
    if confidence < 0.4 or (song.language == "Unknown" and not song.occasion_tags):
        dest_dir = str(base / "Mismatch_Songs")
        return safe_copy(song.file_path, dest_dir)
    
    # --- SIMPLIFIED GENRE-FIRST STRUCTURE ---
    
    # 1. Determine the Primary Genre (Industry)
    genre = "Other"
    if song.industry != "Unknown":
        genre = song.industry
    elif song.language == "English":
        genre = "International"
    elif song.language == "Hindi":
        genre = "Hindi"

    elif song.language != "Unknown":
        genre = song.language # Use language as genre if industry is unknown (e.g. Punjabi)

    # 2. Determine the Sub-Genre (Occasion or Mood)
    sub_genre = "General"
    
    # Priority for Sub-Genre: Mashup/Remix > Occasion > Mood
    is_mashup = any("mashup" in occ.lower() or "remix" in occ.lower() for occ in (song.occasion_tags or []))
    
    if is_mashup:
        sub_genre = "Mashup"

    elif song.occasion_tags or song.mood_tags:
        # Combine all tags for unified priority checking
        all_tags = (song.occasion_tags or []) + (song.mood_tags or [])
        
        # MAIN CATEGORIES: Priority for sub-folders
        priority_list = ["Wedding", "Party", "Sad", "Romantic", "Birthday", "Devotional", "Mashup", "Garba", "Rap", "Chill", "EDM", "Pop", "Rock"]
        
        for p in priority_list:
            if p in all_tags:
                sub_genre = p
                break
        
        # Fallback if tags exist but none of the main categories match
        if sub_genre == "General" and all_tags:
            sub_genre = all_tags[0]

                
    # Sanitize names
    def sanitize(name):
        for char in '<>:"/\\|?*':
            name = name.replace(char, "")
        return name.strip() or "Unknown"

    genre = sanitize(genre)
    sub_genre = sanitize(sub_genre)
    
    # FINAL PATH: sorted song / [Genre] / [Sub-Genre]
    # If the sub-genre is not found, default to 'Bollywood' for Hindi songs
    if genre == "Hindi" and sub_genre == "General":
        sub_genre = "Bollywood"
        
    dest_dir = str(base / genre / sub_genre)
    return safe_copy(song.file_path, dest_dir)



    return safe_copy(song.file_path, dest_dir)
