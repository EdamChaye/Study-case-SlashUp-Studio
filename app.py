import streamlit as st
import os
import base64
import yt_dlp
from pydub import AudioSegment
from openai import OpenAI
from dotenv import load_dotenv
import subprocess

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq

from langchain_core.output_parsers import StrOutputParser


# Load environment variables
load_dotenv()

model = ChatGroq(model="llama-3.1-70b-versatile", temperature=0.5, groq_api_key=os.getenv('resume')) 


# Initialize OpenAI client for Groq API
groq = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

# Function to convert audio file to base64
def audio_to_base64(file):
    with open(file, "rb") as audio_file:
        audio_bytes = audio_file.read()
        base64_audio = base64.b64encode(audio_bytes).decode()
    return base64_audio

# Function to re-encode audio file to opus (ogg) format
def reencode_audio_to_ogg(input_file, output_file="encoded_audio.ogg"):
    command = [
        "ffmpeg", "-y",  # Add the '-y' flag to overwrite without asking
        "-i", input_file, "-vn", "-map_metadata", "-1", 
        "-ac", "1", "-c:a", "libopus", "-b:a", "12k", "-application", "voip", output_file
    ]
    subprocess.run(command, check=True)

# Function to download YouTube video and convert to audio (MP3)
def download_youtube_audio(youtube_url, output_file="youtube_audio.mp3"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': "%(title)s.%(ext)s",  # Use title for the name and mp3 as the extension
        'quiet': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url)
        downloaded_filename = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
    
    if os.path.exists(output_file):
        os.remove(output_file)
    
    os.rename(downloaded_filename, output_file)
    
def process_transcript(transcript):
    # Step 1: Summarize the transcript
    prompt_summary = PromptTemplate(
        input_variables=["transcript"],
        template="Here is a transcript: {transcript} .Write a concise summary of the text. Maintain the language of the original text (if the text is in french, provide the result in french)."
    )
    chain_summary = prompt_summary | model | StrOutputParser()
    summary = chain_summary.invoke({"transcript": transcript})
    
    summary_response=summary

    # Step 2: Generate QCM
    prompt_qcm = PromptTemplate(
        input_variables=["transcript"],
        template="Here is a summary: {transcript} .Generate a multiple-choice questionnaire with 10 questions, each having 3 options. Maintain the language of the original text (if the text is in French, provide the result in French). The final response should be well-structured, with each question and its possible answers clearly formatted on its own line."
    )
    chain_qcm = prompt_qcm | model | StrOutputParser()
    qcm = chain_qcm.invoke({"transcript": transcript})
    
    qcm_response=qcm

    # Step 3: Score QCM with justification
    prompt_score = PromptTemplate(
        input_variables=["qcm"],
        template="Here is a multiple-choice questionnaire: {qcm} .Provide the answers to all questions and include a justification for each answer. Maintain the language of the original text (if the text is in English, provide the result in English). The final response should be well-structured, with each question and its possible answers clearly formatted on its own line. The justification should follow as a paragraph."
    )
    chain_score = prompt_score | model | StrOutputParser()

    scoring = chain_score.invoke({"qcm": qcm})
    
    scoring_response=scoring

    return summary_response, qcm_response, scoring_response

# Streamlit App Setup
st.set_page_config(layout="wide", page_title="🎤 Groq Whisper Fast Transcription")

# Add custom CSS to improve UI styling
st.markdown("""
    <style>
    .main {
        
        padding: 10px;
    }
    .block-container {
        padding-top: 2rem;
    }
    .stButton button {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("🎙️ Edtech.io Generative Quiz Engine ")

# Tabs for File Upload and YouTube Link
tab = st.container()

# Tab 2: YouTube Link to Audio and Transcription
with tab:
    st.header("🎥 Transcribe YouTube Video Audio")
    st.write("Enter a YouTube URL to download and transcribe the audio.")

    youtube_url = st.text_input("🔗 Enter YouTube Video URL")
    if st.button("⬇️ Download and Transcribe"):
        if youtube_url:
            with st.spinner("⚙️ Downloading and processing audio..."):
            # Download YouTube video and extract audio
                download_youtube_audio(youtube_url, "youtube_audio.mp3")

            # Re-encode the downloaded audio to OGG (Opus) format
                reencode_audio_to_ogg("youtube_audio.mp3", "encoded_youtube_audio.ogg")

            # Convert the re-encoded OGG file to base64 for embedding in HTML
                base64_audio = audio_to_base64("encoded_youtube_audio.ogg")

            # Embed the audio file in HTML
                audio_html = f"""
                <audio controls>
                    <source src="data:audio/ogg;base64,{base64_audio}" type="audio/ogg">
                    Your browser does not support the audio element.
                </audio>
                """
                st.subheader("🎶 Downloaded and Re-encoded YouTube Audio")
                st.markdown(audio_html, unsafe_allow_html=True)

            with st.spinner("⏳ Transcribing YouTube audio..."):
                with open("encoded_youtube_audio.ogg", "rb") as audio_file:
                    transcript = groq.audio.transcriptions.create(
                        model="whisper-large-v3",
                        file=audio_file,
                        response_format="text"
                    )
                st.success("🎉 Transcription: " + transcript)    

                summary, qcm, scoring = process_transcript(transcript)
                st.subheader("📋 Transcript ")
                st.text_area("Transcript ", transcript, height=200)
                
                st.subheader("📋 Transcript Summary")
                st.text_area("Transcript Summary", summary, height=200)

                st.subheader("📚 Generated QCM")
                st.text_area("Generated QCM", qcm, height=400)

                st.subheader("✅ QCM Scoring with Justifications")
                st.text_area("QCM Scoring and Justifications", scoring, height=400)
        else:
            st.error("❌ Please enter a valid YouTube URL")
