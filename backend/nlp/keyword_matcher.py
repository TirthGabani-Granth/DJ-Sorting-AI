import re
from nlp.keywords.occasion import OCCASION_KEYWORDS
from nlp.keywords.mood import MOOD_KEYWORDS
from nlp.keywords.industry import INDUSTRY_ARTISTS

def match_tags(text: str, keyword_dict: dict) -> list:
    if not text:
        return []
    text_lower = text.lower()
    matched_tags = set()
    
    for tag, keywords in keyword_dict.items():
        for keyword in keywords:
            # Use regex word boundaries to prevent substring matching (e.g. 'rock' in 'rocky')
            # Escape the keyword to handle any special characters safely
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                matched_tags.add(tag)
                break # Found one keyword for this tag, no need to check others
                
    return list(matched_tags)


def detect_occasion(text: str) -> list:
    return match_tags(text, OCCASION_KEYWORDS)

def detect_mood(text: str) -> list:
    return match_tags(text, MOOD_KEYWORDS)

def detect_industry(text: str) -> str:
    # Industry might have a single dominant return
    matches = match_tags(text, INDUSTRY_ARTISTS)
    if matches:
        return matches[0] # Return the first found industry
    return "Unknown"

def detect_region(industry: str, language: str) -> str:
    indian_industries = ["Bollywood", "Punjabi", "Gujarati", "Tollywood", "Bhojpuri", "Haryanvi"]
    indian_languages = ["Hindi", "Punjabi", "Gujarati", "Tamil", "Telugu", "Bengali", "Marathi", "Urdu"]
    
    if industry in indian_industries:
        return "Indian"
    if industry == "Hollywood":
        return "International"
        
    if language in indian_languages:
        return "Indian"
    if language == "English":
        return "International"
        
    return "Unknown"

def process_text(text: str, current_language: str = "Unknown"):
    occasion_tags = detect_occasion(text)
    mood_tags = detect_mood(text)
    industry = detect_industry(text)
    
    # --- SAFEGUARD: Prevent Hindi songs from being Hollywood ---
    if current_language == "Hindi":
        if industry == "Hollywood" or industry == "Unknown":
            industry = "Bollywood"
            
    region = detect_region(industry, current_language)
    
    return {
        "occasion_tags": occasion_tags,
        "mood_tags": mood_tags,
        "industry": industry,
        "region": region
    }

