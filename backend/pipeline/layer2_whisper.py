import os
import whisper
import warnings
from models.song import SongData
from nlp.keyword_matcher import process_text
from nlp.language_detector import detect_language
import config

# Suppress whisper warnings
warnings.filterwarnings("ignore")

import threading

# Load model globally to avoid loading it per song
_whisper_model = None
_model_lock = threading.Lock()

def get_whisper_model():
    global _whisper_model
    with _model_lock:
        if _whisper_model is None:
            print("Loading Whisper model (this may take a moment on first run)...")
            # 'tiny' or 'base' are best for speed. 'base' is a good middle ground.
            _whisper_model = whisper.load_model("base")
    return _whisper_model

def run_layer2(song: SongData) -> SongData:
    """Executes Layer 2: Whisper Speech to Text + NLP"""
    
    if not os.path.exists(song.file_path):
        return song
        
    try:
        model = get_whisper_model()
        
        # Load exactly 30 seconds of audio starting from second 25
        # Whisper has a load_audio function, we can use librosa to crop or just ffmpeg
        import librosa
        
        # We need to make sure duration doesn't exceed file duration
        if song.duration_seconds and song.duration_seconds < config.AUDIO_START_SEC:
            return song # Too short to process
            
        y, sr = librosa.load(song.file_path, sr=16000, offset=config.AUDIO_START_SEC, duration=config.AUDIO_DURATION_L2)
        
        # Transcribe
        result = model.transcribe(y, fp16=False) # fp16=False for better CPU compatibility if no GPU
        lyrics = result.get("text", "")
        
        if lyrics.strip():
            # Run language detection on lyrics (usually more accurate)
            lyric_lang = detect_language(lyrics)
            if lyric_lang != "Unknown":
                song.language = lyric_lang

            # Run NLP keyword matching on lyrics
            nlp_results = process_text(lyrics, current_language=song.language)
            
            # Merge tags
            song.occasion_tags = list(set(song.occasion_tags + nlp_results["occasion_tags"]))
            song.mood_tags = list(set(song.mood_tags + nlp_results["mood_tags"]))
            
            if song.industry == "Unknown" and nlp_results["industry"] != "Unknown":
                song.industry = nlp_results["industry"]
            
            # Update Region
            song.region = nlp_results["region"]
                
    except Exception as e:
        print(f"Layer 2 (Whisper) failed for {song.file_name}: {e}")
        
    return song
