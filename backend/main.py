from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import sys
from pathlib import Path

# Add the backend directory to sys.path so absolute imports work
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

import config
from services.scanner import scan_folder
from pipeline.orchestrator import process_song
from concurrent.futures import ThreadPoolExecutor

app = FastAPI(title="DJ Song Sorter API")

# Global state to track processing
state = {
    "is_scanning": False,
    "is_processing": False,
    "scanned_files": [],
    "processed_count": 0,
    "total_count": 0,
    "errors": 0
}

def bg_process_songs():
    state["is_processing"] = True
    state["processed_count"] = 0
    state["errors"] = 0
    files_to_process = state["scanned_files"]
    state["total_count"] = len(files_to_process)
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_song, str(f)) for f in files_to_process]
        for future in futures:
            try:
                res = future.result()
                if res.get("status") != "error":
                    state["processed_count"] += 1
                else:
                    state["errors"] += 1
            except Exception as e:
                state["errors"] += 1
                print(f"Error: {e}")
                
    state["is_processing"] = False

@app.get("/")
def read_root():
    return {"message": "DJ Song Sorter API is running"}

@app.post("/api/scan")
def scan_endpoint():
    if state["is_scanning"]:
        return {"status": "scanning already in progress"}
        
    state["is_scanning"] = True
    files = scan_folder(config.INPUT_FOLDER)
    state["scanned_files"] = files
    state["total_count"] = len(files)
    state["is_scanning"] = False
    
    return {"message": f"Found {len(files)} files", "count": len(files)}

@app.post("/api/process")
def process_endpoint(background_tasks: BackgroundTasks):
    if state["is_processing"]:
        return {"status": "Processing already in progress"}
        
    if not state["scanned_files"]:
        return {"status": "No files scanned. Please /api/scan first."}
        
    background_tasks.add_task(bg_process_songs)
    return {"message": "Processing started in background"}

@app.get("/api/status")
def status_endpoint():
    return {
        "is_scanning": state["is_scanning"],
        "is_processing": state["is_processing"],
        "total_files": state["total_count"],
        "processed": state["processed_count"],
        "errors": state["errors"],
        "progress_percent": round((state["processed_count"] / max(1, state["total_count"])) * 100, 2)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
