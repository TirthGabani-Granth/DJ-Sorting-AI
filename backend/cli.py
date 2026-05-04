import sys
from pathlib import Path

# Add the backend directory to sys.path so absolute imports work
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

import config
from services.scanner import scan_folder
from pipeline.orchestrator import process_song
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from pipeline.layer2_whisper import get_whisper_model
from pipeline.layer3_audio import run_layer3 # Just to ensure pre-warm if needed

def main():
    print("DJ Song Sorter - Complete 3-Layer System")
    print(f"Scanning folder: {config.INPUT_FOLDER}")
    
    audio_files = scan_folder(config.INPUT_FOLDER)
    if not audio_files:
        print("No audio files found or directory doesn't exist.")
        return
        
    # Process in batches using ThreadPoolExecutor
    print(f"Processing {len(audio_files)} files...")
    
    # Pre-warm Whisper to avoid race conditions during thread start
    print("Pre-warming AI models...")
    get_whisper_model()
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    # Reduced max_workers to 2 because Whisper and Librosa are CPU heavy
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit tasks
        future_to_file = {executor.submit(process_song, str(file_path)): file_path for file_path in audio_files}
        
        # Process results with progress bar
        for future in tqdm(as_completed(future_to_file), total=len(audio_files), desc="Sorting Songs"):
            file_path = future_to_file[future]
            try:
                result = future.result()
                if result["status"] == "processed":
                    processed_count += 1
                elif result["status"] == "skipped":
                    skipped_count += 1
                else:
                    error_count += 1
            except Exception as exc:
                safe_path = str(file_path).encode("ascii", "ignore").decode()
                print(f'{safe_path} generated an exception: {exc}')
                error_count += 1
                
    print("\n--- Summary ---")
    print(f"Total files: {len(audio_files)}")
    print(f"Processed: {processed_count}")
    print(f"Skipped (already done): {skipped_count}")
    print(f"Errors: {error_count}")
    print(f"Output saved to: {config.OUTPUT_FOLDER}")
    
if __name__ == "__main__":
    main()
