import streamlit as st
import os
import sys
import pandas as pd
from pathlib import Path
import time
import json
import subprocess
import shutil

# Add the backend directory to sys.path so absolute imports work
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.append(str(backend_dir))

import config
from services.database import DatabaseService
from pipeline.orchestrator import process_song
from services.scanner import scan_folder

# Initialize Database
db_service = DatabaseService(config.DATABASE_PATH)

st.set_page_config(page_title="DJ Song Sorter", page_icon="🎵", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 4em;
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        font-size: 18px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff3333;
        border: none;
    }
    .status-card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #3e4150;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎵 DJ Song Sorter AI")
st.markdown("### Simple, Smart Music Organization")
st.markdown("---")

# --- MAIN UI ---
input_folder = st.text_input("📂 Folder to Sort:", value=config.INPUT_FOLDER, help="The folder containing all your mixed songs.")
output_folder = st.text_input("📁 Output Folder:", value=config.OUTPUT_FOLDER, help="Where the sorted music will be copied.")

st.markdown("---")

col1, col2 = st.columns(2)

if col1.button("🚀 Start Sorting Folder"):
    if not os.path.exists(input_folder):
        st.error("Input folder not found! Please check the path.")
    else:
        audio_files = scan_folder(input_folder)
        if not audio_files:
            st.warning("No audio files found in that folder.")
        else:
            st.session_state.sorting_finished = False
            st.info(f"Found {len(audio_files)} songs. Starting the AI Sorter...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.container()
            
            total_files = len(audio_files)
            sorted_categories = set()
            
            for i, file_path in enumerate(audio_files):
                song_name = os.path.basename(file_path)
                status_text.markdown(f"<div class='status-card'>🎧 <b>Processing ({i+1}/{total_files}):</b><br>{song_name}</div>", unsafe_allow_html=True)
                
                # Run the actual sorting
                result = process_song(str(file_path))
                
                # Show result in the log
                if result["status"] in ["processed", "skipped"]:
                    song_data = db_service.get_song(str(file_path))
                    category = "Unknown" if song_data.smart_prediction == "Uncategorized Track" else song_data.smart_prediction
                    sorted_categories.add(category)
                    
                    with log_container:
                        st.write(f"✅ **{song_name}** -> `{category}`")
                
                progress_bar.progress((i + 1) / total_files)
            
            st.session_state.sorting_finished = True
            st.session_state.last_sorted_categories = sorted_categories
            st.success("🎉 All songs sorted successfully!")

if st.session_state.get("sorting_finished"):
    # --- Display Summary of Folders ---
    st.markdown("### 📁 Sorted into these Categories:")
    cols = st.columns(3)
    cats = sorted(list(st.session_state.get("last_sorted_categories", [])))
    for idx, cat in enumerate(cats):
        cols[idx % 3].info(f"📁 {cat}")
    
    st.markdown("---")
    # Button to open folder
    col_a, col_b = st.columns(2)
    if col_a.button("📂 Open Sorted Folder"):
        try:
            os.startfile(output_folder)
            st.toast("Opening folder...")
        except Exception as e:
            st.error(f"Could not open folder automatically: {e}")
            
    # ZIP Download Button
    try:
        zip_path = os.path.join(config.BASE_DIR, "Sorted_Music_Backup")
        if st.session_state.get("sorting_finished"):
            with st.spinner("📦 Zipping folder for download..."):
                shutil.make_archive(zip_path, 'zip', output_folder)
            
            with open(zip_path + ".zip", "rb") as f:
                col_b.download_button(
                    label="🎁 Download All Sorted Songs (.zip)",
                    data=f,
                    file_name="Sorted_Music.zip",
                    mime="application/zip"
                )
    except Exception as e:
        pass

if col2.button("📤 Upload & Sort Files"):
    st.info("Please use the 'Upload' feature in the Sidebar for specific files.")

# --- SIDEBAR FOR UPLOAD ---
with st.sidebar:
    st.header("🎯 Single/Multiple Upload")
    st.write("Upload specific songs from your computer here.")
    uploaded_files = st.file_uploader("Choose audio files", type=["mp3", "wav", "flac", "m4a", "aac", "ogg"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("✨ Sort Uploaded Files"):
            temp_dir = os.path.join(config.BASE_DIR, "temp_uploads")
            os.makedirs(temp_dir, exist_ok=True)
            
            p_bar = st.progress(0)
            for idx, uploaded_file in enumerate(uploaded_files):
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                process_song(temp_file_path)
                p_bar.progress((idx + 1) / len(uploaded_files))
                
                # Clean up
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            
            st.success(f"Sorted {len(uploaded_files)} files!")
            if st.button("Open Output Folder"):
                os.startfile(output_folder)

st.markdown("---")
st.caption("DJ Song Sorter v1.0 — Simple & Powerful AI Automation")
