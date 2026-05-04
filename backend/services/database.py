import os
import json
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from datetime import datetime
from models.song import SongData

Base = declarative_base()

class SongRecord(Base):
    __tablename__ = 'songs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String, unique=True, index=True)
    file_name = Column(String)
    file_format = Column(String)
    file_size_mb = Column(Float)
    
    title = Column(String)
    artist = Column(String)
    album = Column(String)
    year = Column(Integer)
    genre = Column(String)
    duration_seconds = Column(Integer)
    
    language = Column(String)
    occasion_tags = Column(Text) # Stored as JSON string
    mood_tags = Column(Text)     # Stored as JSON string
    industry = Column(String)
    
    bpm = Column(Float)
    bpm_category = Column(String)
    energy = Column(Float)
    bass = Column(Float)
    
    layer_used = Column(Integer)
    confidence_score = Column(Float)
    
    lastfm_tags = Column(Text)
    acoustid_id = Column(String)
    musicbrainz_id = Column(String)
    
    is_scanned = Column(Boolean, default=True)
    is_processed = Column(Boolean, default=False)
    is_copied = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    @property
    def smart_prediction(self) -> str:
        """Synthesizes all tags into a human-readable DJ category prediction."""
        parts = []
        
        # Get occasion tags from JSON string
        import json
        try:
            occ_tags = json.loads(self.occasion_tags) if self.occasion_tags else []
        except:
            occ_tags = []
            
        # 0. SPECIAL PRIORITY: GARBA
        is_garba = any("garba" in occ.lower() or "dandiya" in occ.lower() for occ in occ_tags)
        if is_garba:
            parts.append("Gujarati")
            parts.append("Garba")
        
        # 1. Industry / Origin (if not already handled by Garba)
        if not is_garba:
            if self.industry and self.industry != "Unknown":
                parts.append(self.industry)
            elif self.language and self.language != "Unknown":
                parts.append(self.language)
            
            # 2. Main Occasion
            if occ_tags:
                parts.append(occ_tags[0])
            
        # 3. Main Mood
        try:
            mood_tags = json.loads(self.mood_tags) if self.mood_tags else []
        except:
            mood_tags = []
            
        if mood_tags:
            parts.append(mood_tags[0])
            
        # 4. Energy / Tempo
        if self.bpm_category and self.bpm_category != "Unknown":
            parts.append(f"({self.bpm_category} Tempo)")
            
        if not parts:
            return "Uncategorized Track"
            
        # Clean up duplicates & preserve order
        seen = set()
        clean_parts = []
        for p in parts:
            if p not in seen:
                seen.add(p)
                clean_parts.append(p)
                
        return " ".join(clean_parts)

class DatabaseService:
    def __init__(self, db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.engine = create_engine(f'sqlite:///{db_path}', connect_args={'check_same_thread': False})
        Base.metadata.create_all(self.engine)
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

    def get_song(self, file_path):
        session = self.Session()
        return session.query(SongRecord).filter_by(file_path=file_path).first()
        
    def save_song(self, song: SongData):
        session = self.Session()
        record = self.get_song(song.file_path)
        if not record:
            record = SongRecord(file_path=song.file_path)
            
        record.file_name = song.file_name
        record.file_format = song.file_format
        record.file_size_mb = song.file_size_mb
        record.title = song.title
        record.artist = song.artist
        record.album = song.album
        record.year = song.year
        record.genre = song.genre
        record.duration_seconds = song.duration_seconds
        
        record.language = song.language
        record.occasion_tags = json.dumps(song.occasion_tags)
        record.mood_tags = json.dumps(song.mood_tags)
        record.industry = song.industry
        
        record.bpm = song.bpm
        record.bpm_category = song.bpm_category
        record.energy = song.energy
        record.bass = song.bass
        
        record.layer_used = song.layer_used
        record.confidence_score = song.confidence_score
        
        record.lastfm_tags = song.lastfm_tags
        record.acoustid_id = song.acoustid_id
        record.musicbrainz_id = song.musicbrainz_id
        
        record.is_scanned = song.is_scanned
        record.is_processed = song.is_processed
        record.is_copied = song.is_copied
        
        session.add(record)
        session.commit()
        return record
        
    def get_all_songs(self):
        session = self.Session()
        return session.query(SongRecord).all()
