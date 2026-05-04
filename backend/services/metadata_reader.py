import os
import mutagen
from models.song import SongData

def read_metadata(file_path: str) -> SongData:
    """Reads ID3/Metadata tags from an audio file."""
    file_size_mb = round(os.path.getsize(file_path) / (1024 * 1024), 2)
    file_name = os.path.basename(file_path)
    _, file_ext = os.path.splitext(file_name)
    
    song = SongData(
        file_path=str(file_path),
        file_name=file_name,
        file_format=file_ext.lower().replace('.', ''),
        file_size_mb=file_size_mb
    )
    
    try:
        audio = mutagen.File(file_path, easy=True)
        if audio:
            if 'title' in audio: song.title = audio['title'][0]
            if 'artist' in audio: song.artist = audio['artist'][0]
            if 'album' in audio: song.album = audio['album'][0]
            if 'date' in audio:
                # Try to extract year
                date_str = audio['date'][0]
                if len(date_str) >= 4 and date_str[:4].isdigit():
                    song.year = int(date_str[:4])
            if 'genre' in audio: song.genre = audio['genre'][0]
            
            if hasattr(audio.info, 'length') and audio.info.length:
                song.duration_seconds = int(audio.info.length)
                
    except Exception as e:
        print(f"Failed to read metadata for {file_name}: {e}")
        
    return song
