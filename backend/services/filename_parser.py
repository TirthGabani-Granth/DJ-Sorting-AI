import re

def parse_filename(filename: str):
    """
    Parses the filename to extract potential title, artist, and year.
    Common patterns: "Title - Artist.mp3" or "Artist - Title.mp3"
    """
    # 1. Extract Year (Look for 4 digits like 1981 or 2024 in brackets or parentheses)
    year = 0
    year_match = re.search(r'\((\d{4})\)|\[(\d{4})\]', filename)
    if year_match:
        year = int(year_match.group(1) or year_match.group(2))

    # Remove extension
    name_without_ext = re.sub(r'\.[^.]+$', '', filename)
    
    # Remove common junk from filenames (e.g., bitrates, websites)
    clean_name = re.sub(r'\(.*?\)|\[.*?\]|_|- \d+kbps|www\..*?\.com', ' ', name_without_ext)
    
    # Split by hyphen or pipe
    parts = re.split(r' - | \| | _ ', clean_name)
    
    artist = "Unknown"
    title = "Unknown"
    
    if len(parts) >= 2:
        title = parts[0].strip()
        artist = parts[1].strip()
    else:
        title = clean_name.strip()
        
    return title, artist, year

