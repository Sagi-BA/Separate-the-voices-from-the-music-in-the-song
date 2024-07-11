import os
import streamlit as st

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

def upload_file():
    st.header("העלאת קובץ שיר")

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    uploaded_file_path = None

    uploaded_file = st.file_uploader("בחר קובץ שיר (MP3, WAV, MPEG, - מקסימום 5MB)", type=["mp3", "wav", "mpeg"], accept_multiple_files=False)
    
    if uploaded_file is not None:
        if uploaded_file.size > MAX_FILE_SIZE:
            st.error(f"הקובץ גדול מדי. הגודל המקסימלי המותר הוא 50MB. גודל הקובץ שלך: {uploaded_file.size / 1024 / 1024:.2f}MB")
        else:
            try:
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                uploaded_file_path = file_path
                st.success(f"הקובץ {uploaded_file.name} הועלה בהצלחה.")
            except Exception as e:
                st.error(f"אירעה שגיאה בעת העלאת הקובץ: {str(e)}")

    return uploaded_file_path