from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from nlp.keywords.language import LANGUAGE_KEYWORDS

# Ensure consistent results
DetectorFactory.seed = 0

LANGUAGE_MAP = {
    'hi': 'Hindi',
    'en': 'English',
    'gu': 'Gujarati',
    'pa': 'Punjabi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'bn': 'Bengali',
    'mr': 'Marathi',
    'ur': 'Urdu'
}

def detect_language(text: str) -> str:
    if not text or len(text.strip()) < 3:
        return "Unknown"
        
    text_lower = text.lower()
    
    import re
    # Priority 1: Keyword Matching (Explicitly mentioned language)
    for lang, keywords in LANGUAGE_KEYWORDS.items():
        for kw in keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text_lower):
                return lang

                
    # Priority 2: AI/Heuristic detection
    try:
        lang_code = detect(text)
        return LANGUAGE_MAP.get(lang_code, "Unknown")
    except LangDetectException:
        return "Unknown"

