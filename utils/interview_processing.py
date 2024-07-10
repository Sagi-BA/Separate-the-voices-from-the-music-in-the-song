import streamlit as st
import os
import base64
from dotenv import load_dotenv
from utils.voice_music_separator import VoiceMusicSeparator

# Load environment variables
load_dotenv()

# Define the path for the temporary audio files
TEMP_AUDIO_DIR = os.path.join(os.getcwd(), "temp_audio")

# Ensure the temporary directory exists
if not os.path.exists(TEMP_AUDIO_DIR):
    os.makedirs(TEMP_AUDIO_DIR)

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}" class="download-link">הורד {file_label}</a>'
    return href

def display_audio_with_download(file_path, label, icon):
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown(f'<i class="fas {icon} fa-2x"></i>', unsafe_allow_html=True)
    with col2:
        st.audio(file_path, format="audio/wav")
    with col3:
        st.markdown(get_binary_file_downloader_html(file_path, label), unsafe_allow_html=True)

def process_interviews(audio_file_path):
    if 'processed' not in st.session_state:
        st.session_state.processed = False

    if not st.session_state.processed:
        try:
            with st.spinner('נא להמתין מבצע עיבוד...'):
                separator = VoiceMusicSeparator()            
                voice_path, music_path = separator.process_file(audio_file_path)
                st.success("הפרדת הקולות מהמוזיקה בוצעה בהצלחה!")
                st.session_state.voice_path = voice_path
                st.session_state.music_path = music_path
                st.session_state.processed = True
        except Exception as e:
            st.error(f"שגיאה בעיבוד הקובץ: {str(e)}")
            return None

    st.subheader("תוצאות העיבוד")
    
    st.write("קובץ מקורי:")
    display_audio_with_download(audio_file_path, "קובץ מקורי", "fa-file-audio")
    
    st.write("קובץ קול מופרד:")
    display_audio_with_download(st.session_state.voice_path, "קובץ קול", "fa-microphone")
    
    st.write("קובץ מוזיקה מופרד:")
    display_audio_with_download(st.session_state.music_path, "קובץ מוזיקה", "fa-music")

    return audio_file_path

def cleanup_files():
    # Clean up voice file
    if 'voice_path' in st.session_state:
        try:
            if os.path.exists(st.session_state.voice_path):
                os.remove(st.session_state.voice_path)
            del st.session_state.voice_path
        except Exception as e:
            print(f"Error removing voice file: {e}")

    # Clean up music file
    if 'music_path' in st.session_state:
        try:
            if os.path.exists(st.session_state.music_path):
                os.remove(st.session_state.music_path)
            del st.session_state.music_path
        except Exception as e:
            print(f"Error removing music file: {e}")

    # Clean up original uploaded file
    if 'file_path' in st.session_state and st.session_state.file_path:
        try:
            if os.path.exists(st.session_state.file_path):
                os.remove(st.session_state.file_path)
            del st.session_state.file_path
        except Exception as e:
            print(f"Error removing uploaded file: {e}")

    st.session_state.processed = False
