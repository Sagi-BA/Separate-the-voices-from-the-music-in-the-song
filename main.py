# [![Watch the video](https://img.youtube.com/vi/vdaXGeOyvbE/maxresdefault.jpg)](https://youtu.be/vdaXGeOyvbE)

![image](https://i.imgur.com/FXFMBi4.jpeg)

import asyncio
import streamlit as st

from utils.init import initialize
from utils.counter import initialize_user_count, increment_user_count, decrement_user_count, get_user_count
from utils.file_upload import upload_file
from utils.interview_processing import process_interviews, cleanup_files
from utils.TelegramSender import TelegramSender

UPLOAD_DIR = "uploads"

# Initialize TelegramSender
if 'telegram_sender' not in st.session_state:
    st.session_state.telegram_sender = TelegramSender()

# Increment user count if this is a new session
if 'counted' not in st.session_state:
    st.session_state.counted = True
    increment_user_count()

# Initialize user count
initialize_user_count()

# Register a function to decrement the count when the session ends
def on_session_end():
    decrement_user_count()

st.session_state.on_session_end = on_session_end

def start_over():
    keys_to_keep = ['counted', 'on_session_end', 'telegram_sender']
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    st.session_state.active_tab = None
    print("Session state cleared for Start Over")

def main():
    header_content, footer_content = initialize()
    st.markdown(header_content)

    if st.button("התחל מחדש", use_container_width=True):
        start_over()

    file_path = upload_file()
    if file_path:
        st.session_state['file_path'] = file_path

    if st.button("חלץ קולות ומוזיקה מהשיר", use_container_width=True):
        if 'file_path' not in st.session_state or not st.session_state['file_path']:
            st.error("נא להעלות קובץ תחילה.")
        else:
            original_audio_path = process_interviews(st.session_state['file_path'])
            if original_audio_path:
                asyncio.run(send_telegram_audio(original_audio_path))
            
            # Call cleanup_files() only after processing is complete
            cleanup_files()

    user_count = get_user_count(formatted=True)
    footer_with_count = f"{footer_content}\n\n<p class='user-count'>סה\"כ משתמשים: {user_count}</p>"
    st.markdown(footer_with_count, unsafe_allow_html=True)

async def send_telegram_audio(audio_path):
    sender = st.session_state.telegram_sender
    try:
        await sender.send_audio(audio_path, "Separate the voices from the music in the song")
    finally:
        await sender.close_session()

if __name__ == "__main__":
    main()
