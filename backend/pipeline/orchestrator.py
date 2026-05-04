import os
import config
from services.database import DatabaseService
from services.file_copier import copy_song_to_folders
from pipeline.layer1_metadata import run_layer1
from pipeline.layer2_whisper import run_layer2
from pipeline.layer3_audio import run_layer3

db_service = DatabaseService(config.DATABASE_PATH)

def safe_print(msg):
    """Helper to print strings safely to the Windows terminal."""
    try:
        print(msg)
    except UnicodeEncodeError:
        # Fallback for Windows terminals that don't support special chars
        print(msg.encode('ascii', 'ignore').decode('ascii'))

def process_song(file_path: str):
    """Orchestrates the pipeline for a single song."""
    
    # --- CHECK SQLITE FIRST ---
    existing_record = db_service.get_song(file_path)
    if existing_record and existing_record.is_processed and existing_record.is_copied:
        # Reconstruct prediction for logging
        safe_print(f"[SKIP] {os.path.basename(file_path)} -> Already sorted as: {existing_record.smart_prediction}")
        return {"status": "skipped", "file": os.path.basename(file_path)}
        
    try:
        # --- LAYER 1 ---
        song = run_layer1(file_path)
        song.is_scanned = True
        
        confidence = song.calculate_confidence()
        
        if confidence >= config.CONFIDENCE_L1:
            song.layer_used = 1
            song.is_processed = True
        else:
            # --- LAYER 2 ---
            song = run_layer2(song)
            confidence = song.calculate_confidence()
            
            if confidence >= config.CONFIDENCE_L2:
                song.layer_used = 2
                song.is_processed = True
            else:
                # --- LAYER 3 ---
                song = run_layer3(song)
                song.layer_used = 3
                song.is_processed = True
                confidence = song.calculate_confidence()
            
        # --- COPY STEP ---
        if song.is_processed:
            copy_success = copy_song_to_folders(song, config.OUTPUT_FOLDER)
            if copy_success:
                song.is_copied = True
                
        # --- SAVE TO DB ---
        db_service.save_song(song)
        
        safe_print(f"[OK] {os.path.basename(file_path)} -> {song.smart_prediction} (Layer {song.layer_used})")
        
        return {"status": "processed", "file": os.path.basename(file_path), "layer": song.layer_used, "confidence": confidence}
        
    except Exception as e:
        safe_print(f"Error processing {os.path.basename(file_path)}: {str(e)}")
        return {"status": "error", "file": os.path.basename(file_path), "error": str(e)}
