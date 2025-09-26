import streamlit as st
import yt_dlp
import os
import re
from yt_dlp.utils import DownloadError

# --- Custom CSS for Stylish Buttons ---
st.markdown("""
<style>
/* Style for the main action button ('Fetch Video') */
div.stButton > button:first-child {
    background: linear-gradient(90deg, #FF4B2B, #FF416C);
    color: white;
    font-size: 18px;
    font-weight: bold;
    padding: 12px 30px;
    border: none;
    border-radius: 50px; /* Makes it a pill shape */
    box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease-in-out;
    width: 100%;
}

div.stButton > button:first-child:hover {
    transform: scale(1.03);
    box-shadow: 0 6px 20px 0 rgba(0, 0, 0, 0.2);
}

/* Style for the file download button */
div.stDownloadButton > button:first-child {
    background: linear-gradient(90deg, #FF4B2B, #FF416C);
    color: white;
    font-size: 18px;
    font-weight: bold;
    padding: 12px 30px;
    border: none;
    border-radius: 50px;
    box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease-in-out;
    width: 100%;
}

div.stDownloadButton > button:first-child:hover {
    transform: scale(1.03);
    box-shadow: 0 6px 20px 0 rgba(0, 0, 0, 0.2);
}
</style>
""", unsafe_allow_html=True)

# --- Helper Function to Create Safe Filenames ---
def sanitize_filename(text):
    """
    Removes or replaces illegal filename characters from text.
    """
    return re.sub(r'[\\/*?:"<>|]', "", text)

# --- Core yt-dlp Download Function ---
def download_tiktok_video(video_url):
    """
    Downloads a TikTok video using yt-dlp.
    Returns a tuple: (file_path, error_message).
    """
    try:
        # Extract video metadata first
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            username = info.get('uploader', 'unknown_user')
            title = info.get('title', 'tiktok_video')
            title = sanitize_filename(title.strip())[:50]  # Limit to 50 chars

            filename = f"{username}({title}).mp4"

        # Download options
        ydl_opts = {
            'outtmpl': filename,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'quiet': True
        }

        # Download video using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            
        return filename, None

    except DownloadError:
        user_friendly_error = "❌ Invalid URL or private video. Please check the URL and try again."
        return None, user_friendly_error
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        user_friendly_error = "❌ An unexpected error occurred. Please try again later."
        return None, user_friendly_error

# --- Streamlit User Interface ---
st.set_page_config(page_title="TikTok Video Downloader", layout="centered")

st.title("🎬 Free TikTok Video Downloader")
st.write("Paste a TikTok video URL below to download a **high-quality** video without any watermark.")

url = st.text_input("Enter **TikTok** Video URL:", placeholder="https://www.tiktok.com/@user/video/123...", label_visibility="collapsed")

show_preview = st.toggle("Show video preview", value=True, help="If enabled, a preview of the video will be shown after loading.")

if st.button("⬇️ Fetch Video"):
    if url:
        with st.spinner("Fetching and downloading your video... Please wait."):
            video_path, error_msg = download_tiktok_video(url)

            if error_msg:
                st.error(error_msg)
            elif video_path and os.path.exists(video_path):
                st.success("✅ Video loaded successfully!")

                with open(video_path, "rb") as file:
                    video_bytes = file.read()
                
                if show_preview:
                    st.video(video_bytes)

                spacer_col, button_col = st.columns([2, 1])

                with button_col:
                    st.download_button(
                        label="Download Video",
                        data=video_bytes,
                        file_name=os.path.basename(video_path),
                        mime="video/mp4"
                    )

                os.remove(video_path)
    else:
        st.warning("Please enter a TikTok URL.")
