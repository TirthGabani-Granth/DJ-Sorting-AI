from dataclasses import dataclass, field
from typing import List

@dataclass
class SongData:
    file_path: str
    file_name: str
    file_format: str
    file_size_mb: float
    
    title: str = "Unknown"
    artist: str = "Unknown"
    album: str = "Unknown"
    year: int = 0
    genre: str = "Unknown"
    duration_seconds: int = 0
    
    language: str = "Unknown"
    region: str = "Unknown"  # Indian or International
    occasion_tags: List[str] = field(default_factory=list)
    mood_tags: List[str] = field(default_factory=list)
    industry: str = "Unknown"
    
    bpm: float = 0.0
    bpm_category: str = "Unknown"
    energy: float = 0.0
    bass: float = 0.0
    
    layer_used: int = 0
    confidence_score: float = 0.0
    
    lastfm_tags: str = "{}"
    acoustid_id: str = ""
    musicbrainz_id: str = ""
    
    is_scanned: bool = False
    is_processed: bool = False
    is_copied: bool = False
    
    def calculate_confidence(self) -> float:
        score = 0.0
        if self.language != "Unknown":    
            score += 0.20
        if self.region != "Unknown":
            score += 0.15
        if self.occasion_tags:            
            score += 0.25
        if self.mood_tags:                
            score += 0.20
        if self.industry != "Unknown":    
            score += 0.10
        if self.year and self.year > 0:                     
            score += 0.10
            
        # Use the highest score (preserves manual boosts from Layer 1)
        final_score = max(score, self.confidence_score)
        self.confidence_score = final_score
        return final_score

        
    @property
    def smart_prediction(self) -> str:
        """Synthesizes all tags into a human-readable DJ category prediction."""
        parts = []
        
        # 0. SPECIAL PRIORITY: GARBA
        is_garba = any("garba" in occ.lower() or "dandiya" in occ.lower() for occ in (self.occasion_tags or []))
        if is_garba:
            parts.append("Gujarati")
            parts.append("Garba")
            if self.occasion_tags:
                parts.extend([o for o in self.occasion_tags if o.lower() not in ["garba", "dandiya"]])
        
        # 1. Region & Industry
        if not is_garba:
            if self.language and self.language != "Unknown":
                parts.append(self.language)
            if self.region and self.region != "Unknown":
                parts.append(f"[{self.region}]")
            if self.industry and self.industry != "Unknown":
                parts.append(self.industry)
            
            # 2. Occasions
            if self.occasion_tags:
                parts.extend(self.occasion_tags)
            
        # 3. Main Mood (Prioritize descriptive moods over technical ones)
        if self.mood_tags:
            priority_moods = ["Sad", "Romantic", "Party", "Devotional", "Chill", "Wedding"]
            selected_mood = self.mood_tags[0]
            for pm in priority_moods:
                if pm in self.mood_tags:
                    selected_mood = pm
                    break
            parts.append(selected_mood)

            
        # 4. Energy / Tempo
        if self.bpm_category and self.bpm_category != "Unknown":
            parts.append(f"({self.bpm_category} Tempo)")
            
        if not parts:
            return "Uncategorized Track"
            
        # Clean up duplicates & preserve order
        seen = set()
        clean_parts = []
        for p in parts:
            p_clean = str(p).strip()
            if p_clean.lower() not in seen:
                seen.add(p_clean.lower())
                clean_parts.append(p_clean)
                
        return " > ".join(clean_parts)
