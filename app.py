import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import base64

load_dotenv()  
import os

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are Yotube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 250 words. Please provide the summary of the text given here:  """

## getting the transcript data from yt videos
def extract_transcript_details(youtube_video_url, language="en"):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e

## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

def get_binary_file_downloader_html(bin_file, file_label='File', file_name='file'):
    """
    Generates a link to download the given binary file.
    
    Parameters:
        bin_file: bytes - The binary file to download.
        file_label: str - Label of the download link (default: 'File').
        file_name: str - Name of the file to download (default: 'file').
    
    Returns:
        str: HTML code for downloading the file.
    """
    # Convert the binary file to base64
    bin_file_base64 = base64.b64encode(bin_file.encode()).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_file_base64}" download="{file_name}">{file_label}</a>'
    return href

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

language = st.selectbox("Select Video Language:", ["en", "es", "fr", "de", "it", "ja", "ko", "pt", "ru", "zh-CN"])

# Additional functionalities
max_summary_length = st.number_input("Maximum Summary Length (words):", min_value=50, max_value=500, value=250)

if youtube_link:
    try:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except IndexError:
        st.warning("Invalid YouTube URL. Please enter a valid URL.")

if st.button("Get Detailed Notes"):
    try:
        transcript_text = extract_transcript_details(youtube_link, language)
    except Exception as e:
        st.error(f"Error extracting transcript: {str(e)}")
        st.stop()

    if transcript_text:
        st.markdown("## Original Transcript:")
        st.write(transcript_text)

        summary = generate_gemini_content(transcript_text, prompt)
        
        summaries = summary.split("\n")
        
        st.markdown("## Detailed Notes:")
        for s in summaries:
            st.write(s)

        st.markdown("## Export the notes:")
        download_text = "\n".join(summaries)
        st.markdown(get_binary_file_downloader_html(download_text, file_label="Download Text", file_name="summary.txt"), unsafe_allow_html=True)
