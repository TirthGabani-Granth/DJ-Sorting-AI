import os
import librosa
import numpy as np
from models.song import SongData
import config
import warnings

warnings.filterwarnings("ignore")

def map_audio_to_mood(bpm, energy, bass):
    mood = []
    
    # BPM category
    if bpm < 80:
        bpm_category = "Slow-below-80"
    elif bpm < 120:
        bpm_category = "Mid-80-to-120"
    elif bpm < 150:
        bpm_category = "Fast-120-to-150"
    else:
        bpm_category = "VeryFast-above-150"

    # Mood from audio features
    if energy > 0.7 and bpm > 120:
        mood.append("Party-Dance")
    if energy < 0.4 and bpm < 90:
        mood.append("Romantic")
    if energy < 0.3 and bpm < 80:
        mood.append("Chill")
    if bass > 0.7 and energy > 0.6:
        mood.append("Bass-Heavy")
    if energy < 0.4 and bpm < 70:
        mood.append("Sad")
        
    return mood, bpm_category

def run_layer3(song: SongData) -> SongData:
    """Executes Layer 3: Audio analysis using librosa"""
    if not os.path.exists(song.file_path):
        return song
        
    try:
        # Load audio from 25th second, max 60 seconds
        if song.duration_seconds and song.duration_seconds < config.AUDIO_START_SEC:
            return song
            
        y, sr = librosa.load(song.file_path, offset=config.AUDIO_START_SEC, duration=config.AUDIO_DURATION_L3)
        
        # Extract BPM (Tempo)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        
        # Librosa sometimes returns an array for tempo
        if isinstance(tempo, np.ndarray):
            tempo = tempo[0]
            
        song.bpm = float(tempo)
        
        # Extract Energy (RMS)
        rms = librosa.feature.rms(y=y)
        song.energy = float(np.mean(rms))
        
        # Extract Bass
        # To get bass, we can analyze lower frequencies of the spectrogram
        S = np.abs(librosa.stft(y))
        freqs = librosa.fft_frequencies(sr=sr)
        bass_idx = np.where(freqs < 150)[0] # Frequencies below 150Hz
        bass_energy = np.mean(S[bass_idx, :])
        song.bass = float(bass_energy)
        
        # Normalize energy and bass (rough approximation 0 to 1)
        # Typically RMS is < 1 for normalized audio, but bass energy can vary.
        # We will apply a sigmoid or simple scaling for the mapping logic
        norm_energy = min(1.0, song.energy * 5) # rough scaling
        norm_bass = min(1.0, song.bass / 10)    # rough scaling
        
        # Map to mood and BPM category
        audio_moods, bpm_cat = map_audio_to_mood(song.bpm, norm_energy, norm_bass)
        
        song.bpm_category = bpm_cat
        song.mood_tags = list(set(song.mood_tags + audio_moods))
        
    except Exception as e:
        print(f"Layer 3 (Audio Analysis) failed for {song.file_name}: {e}")
        
    return song
