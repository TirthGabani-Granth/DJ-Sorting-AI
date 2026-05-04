# DJ Song Sorter: Implementation & Optimization Guide

## 1. System Architecture (The 3-Layer Pipeline)
The system uses a confidence-based "Waterfall" model to ensure maximum accuracy while maintaining high speed.

### Layer 1: Metadata & NLP (The "Brain")
- **Priority**: Language -> Industry -> Category.
- **Key Feature**: **Word Boundary Regex Matching**. This prevents false matches (e.g., "Rocky" no longer matches "Rock").
- **Safeguard**: **Hindi-First Protection**. If a song is detected as Hindi, it is blocked from being categorized as "International" or "Hollywood".
- **Database**: Uses `songs_v4.db` to prevent redundant processing.

### Layer 2: Whisper AI (The "Linguist")
- **Action**: Listens to the first 30 seconds of the song and transcribes lyrics.
- **Use Case**: Used only when Layer 1 is unsure. It confirms the language and looks for mood-related keywords in the lyrics.

### Layer 3: Librosa Analysis (The "DJ")
- **Action**: Analyzes BPM, RMS (Energy), and Spectral Centroid.
- **Use Case**: Final verification for categories like "Party" (High BPM/Energy) or "Sad" (Low BPM/Energy).

---

## 2. Folder Hierarchy
The system enforces a clean, DJ-friendly 2-level structure:
- `sorted song / Hindi / Bollywood / [Category]`
- `sorted song / International / [Category]`
- `sorted song / Gujarati / [Category]`
- `sorted song / Mashup` (For all remixes and nonstop mixes)

---

## 3. Future Performance Optimizations

### Speed Improvements
- **`faster-whisper`**: Replace the current `openai-whisper` with `faster-whisper` for a 4x speed boost on Layer 2.
- **Parallel Processing**: Update `orchestrator.py` to use `concurrent.futures` for processing multiple songs at once.
- **Skip Layer 2 for "Trifecta" Matches**: If Title, Artist, and Filename all suggest the same category, Layer 2 should be skipped entirely to save time.

### Accuracy Improvements
- **Artist Database Expansion**: For 100% accuracy, we should continue adding regional artists to `backend/nlp/keywords/industry.py`. I have already added the biggest ones (Arijit, Geeta Rabari, etc.), but adding more local DJs will help.
- **Year Detection**: Use the (1981) type patterns in filenames to automatically tag "90s Hits" or "Old is Gold" categories.
- **Dynamic Thresholds**: Lower the confidence threshold for high-quality audio files (320kbps) as they are easier for AI to analyze.

---

## 4. Maintenance
- **Keywords**: To add new categories, simply edit `backend/nlp/keywords/`.
- **Database Reset**: If you change categories, update `DATABASE_PATH` in `config.py` to start a fresh run.
- **Logs**: Always check the terminal output for `[OK]` vs `[SKIP]` to monitor the system's decisions.
