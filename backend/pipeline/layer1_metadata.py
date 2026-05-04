from services.metadata_reader import read_metadata
from services.filename_parser import parse_filename
from nlp.keyword_matcher import process_text
from nlp.language_detector import detect_language
from models.song import SongData
from apis.jiosaavn import get_jiosaavn_info
from apis.lastfm import get_lastfm_tags
from apis.musicbrainz import get_musicbrainz_info

def run_layer1(file_path: str) -> SongData:
    """Executes Layer 1: Metadata + Filename + NLP"""
    
    # 1. Read metadata
    song = read_metadata(file_path)
    
    # 2. If tags are "Unknown", fallback to filename parsing
    parsed_title, parsed_artist, parsed_year = parse_filename(song.file_name)
    
    if song.title == "Unknown":
        song.title = parsed_title
    if song.artist == "Unknown":
        song.artist = parsed_artist
    if (not song.year or song.year == 0) and parsed_year != 0:
        song.year = parsed_year

        
    # Prepare text for NLP (Include filename as it often contains the most useful keywords)
    text_blob = f"{song.file_name} {song.title} {song.artist} {song.genre} {song.album}"

    
    # 3. Run Language Detection (Detect language FIRST)
    song.language = detect_language(text_blob)

    # 4. Run NLP keyword matching (Now knows the language)
    nlp_results = process_text(text_blob, current_language=song.language)
    song.occasion_tags = nlp_results["occasion_tags"]
    song.mood_tags = nlp_results["mood_tags"]
    song.industry = nlp_results["industry"]
    song.region = nlp_results["region"]


    
    # 5. APIs (Optional Enrichment)
    mb_info = get_musicbrainz_info(file_path)
    if mb_info:
        song.acoustid_id = mb_info.get("acoustid_id", "")
        song.musicbrainz_id = mb_info.get("musicbrainz_id", "")
        
    js_info = get_jiosaavn_info(song.title, song.artist)
    if js_info:
        if song.language == "Unknown" and js_info.get("language"):
            song.language = js_info.get("language").capitalize()
        if (song.year == 0 or not song.year) and js_info.get("year"):
            song.year = int(js_info.get("year"))
            
    song.lastfm_tags = get_lastfm_tags(song.title, song.artist)
    
    # 6. Final Region Re-evaluation
    from nlp.keyword_matcher import detect_region
    song.region = detect_region(song.industry, song.language)
    
    # --- HIGH ACCURACY BOOST ---
    # If we found Language, Industry AND (Occasion or Mood) in the title/filename, 
    # we are very confident. We can skip Whisper/Audio layers.
    has_lang = song.language != "Unknown"
    has_ind = song.industry != "Unknown"
    has_occ = len(song.occasion_tags) > 0
    has_mood = len(song.mood_tags) > 0
    
    # If we have the "Trifecta" (Lang, Industry, and a tag) in the title/filename
    if has_lang and has_ind and (has_occ or has_mood):
        # Force high confidence to skip next layers
        song.confidence_score = 0.88
    elif song.language == "Hindi" and (has_occ or has_mood):
        # High confidence for Hindi songs with clear category tags
        song.confidence_score = 0.85
    elif has_lang and (has_occ and has_mood):
        # Also high confidence if we have lang and two types of tags
        song.confidence_score = 0.82
        
    return song

