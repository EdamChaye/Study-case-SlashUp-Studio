# Edtech.io Generative Quiz Engine

## Project Overview

This project addresses the challenge of creating an automated learning assessment tool for the Edtech.io e-learning platform. The solution develops a generative quiz engine that can:
- Summarize video course content
- Generate multiple-choice questionnaires
- Automatically grade and provide justifications for quiz answers

## Key Technologies

- Python
- Streamlit
- Groq API (Whisper & LLaMA)
- LangChain
- yt-dlp
- OpenAI Python Library

## Project Workflow

1. **Video Input**: 
  - User provides a YouTube video URL
  - Audio is downloaded and extracted

2. **Transcription**:
  - Audio converted to text using Whisper
  - Transcription processed by language model

3. **Content Analysis**:
  - Generate summary of course content
  - Create multiple-choice questionnaire
  - Produce automated scoring with justifications

## Technical Architecture

### Key Components
- **Transcription**: Groq Whisper API for audio-to-text conversion
- **Natural Language Processing**: Langchain with Groq's LLaMA 3.1 70B model (Using LCEL (langchain expression language), prompt engineering + llm +StrOutputParser to to garantee a good structured output from the model)
- **Web Interface**: Streamlit for user interaction

## Installation

### Prerequisites
- Python 3.10+
- Groq API Key
- ffmpeg

### Setup Steps
1. Clone the repository
2. Install dependencies:
  ```bash
  pip install -r requirements.txt
3. Run the application : 
  streamlit run app.py

### How to get GROQ-API

- Groq API is totally free and it provides the fastest inference in LLMs.
1. Navigate to https://groq.com/
2. Go to 'Developers' section and then Click at 'FREE API KEY' and then create an api key
3. Add the 2 api keys created to .env file

### ffmpeg configuration
1. Install ffmpeg from https://www.ffmpeg.org/download.html
2. Extract the zip file in \:c directory
3. Go the extracted file and click on 'bins' folder
4. Copy path 
5. Add path to environment variables (system's PATH)

## Features 

1. Automatic video content transcription
2. Intelligent course summary generation
3. 10-question multiple-choice quiz creation
4. Automated quiz grading with detailed justifications

## Project structure 

ETUDE DE CAS/
│
├── .env                # Contains the Groq API keys
├── app.py              # Main Python file for the Streamlit app
├── requirements.txt    # Python dependencies
├── python_env.yaml     # Python dependencies
└── README.md           # This README file