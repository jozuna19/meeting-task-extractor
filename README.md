Meeting Task Extractor

AI-powered web app that transcribes meeting recordings and automatically extracts structured action items with owners and deadlines.

Built with Python, Streamlit, OpenAI Whisper, and Anthropic Claude.

Overview

This application allows users to upload an audio or video recording of a meeting and automatically:

Transcribe speech to text using OpenAI Whisper

Extract action items using Claude

Display tasks with responsible parties and deadlines

Export tasks as CSV or TXT

The goal is to turn unstructured conversations into clear, actionable outputs.

Live Demo

Deployed on Streamlit Cloud.

Upload supported audio formats such as:

mp3

m4a

wav

mp4

ogg

webm

flac

Note: Microphone recording is supported in the local development version only. The deployed cloud version uses file upload due to server-side audio hardware limitations.

Features

Audio/video file upload

Automatic transcription (Whisper API)

AI-powered task extraction (Claude API)

Structured task formatting:

What needs to be done

Who is responsible

Deadline or timeframe

Interactive checkboxes

Export to CSV

Export to TXT

Clean dark-mode UI

Tech Stack

Python

Streamlit

OpenAI Whisper API

Anthropic Claude API

python-dotenv

How It Works

User uploads an audio file

File is temporarily stored server-side

Whisper generates a transcript

Claude analyzes the transcript and extracts action items

Results are parsed into structured task objects

Tasks are displayed and available for export

Local Development Setup

Clone the repository:

git clone https://github.com/your-username/meeting-task-extractor.git
cd meeting-task-extractor

Install dependencies:

pip install -r requirements.txt

Create a .env file:

OPENAI_API_KEY="your_openai_key"
ANTHROPIC_API_KEY="your_anthropic_key"

Run the app:

streamlit run app.py
Deployment

This project is deployed using Streamlit Cloud.

Secrets are stored securely using Streamlit’s built-in Secrets manager in TOML format:

OPENAI_API_KEY = "your_openai_key"
ANTHROPIC_API_KEY = "your_anthropic_key"
Future Improvements

Browser-based microphone recording

Speaker diarization (identify who said what)

Notion/Todoist integration

Automatic calendar follow-up generation

PDF export

Meeting summary generation

Why This Project

This project demonstrates:

API integration across multiple AI providers

File handling and temporary storage

Structured LLM prompting and response parsing

Cloud deployment

Production-style secrets management

Real-world AI workflow automation
