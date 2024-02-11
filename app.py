import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # load all the environment variables
import os
import google.generativeai as genai

from youtube_transcript_api import YouTubeTranscriptApi

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
        
        # Split the summary into lines
        summaries = summary.split("\n")
        
        st.markdown("## Detailed Notes:")
        for s in summaries:
            st.write(s)
