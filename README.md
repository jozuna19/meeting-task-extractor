# Meeting Task Extractor

An AI-powered tool that automatically transcribes meetings and calls, then extracts actionable tasks — so you never miss a follow-up again.

---

## Features

- Upload audio or video files — supports MP3, MP4, WAV, M4A, OGG, WEBM, FLAC, CAF, and more
- Live microphone recording — record directly from your browser
- Auto format conversion — unsupported formats are automatically converted via ffmpeg
- Full transcript view — collapsible transcript for every recording
- Smart task extraction — identifies what needs to be done, who is responsible, and any deadlines
- Interactive checkboxes — check off tasks as you complete them
- Export to CSV or TXT — save and share your task list

---

## Tech Stack

- UI: Streamlit
- Transcription: OpenAI Whisper API
- Task Extraction: Anthropic Claude API
- Audio Recording: sounddevice + scipy
- Format Conversion: ffmpeg

---

## Getting Started

### 1. Clone the repo

git clone https://github.com/jozuna19/meeting-task-extractor.git
cd meeting-task-extractor

### 2. Install dependencies

pip install streamlit openai anthropic sounddevice scipy python-dotenv
brew install ffmpeg

### 3. Add your API keys

Create a .env file in the project root:

OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here

You will need an OpenAI account and an Anthropic account with billing enabled. Both offer low-cost pay-as-you-go pricing — a typical meeting costs less than $0.05 to process.

### 4. Run the app

streamlit run app.py

Open your browser to http://localhost:8501 and you are good to go.

---

## Project Structure

meeting-task-extractor/
├── app.py            # Main Streamlit app
├── .env              # API keys (not committed to git)
├── .gitignore        # Excludes .env and temp files
└── README.md

---

## Important: Keep your API keys safe

Make sure your .env file is listed in .gitignore before pushing to GitHub:

.env
*.wav
*_converted.mp3
__pycache__/

---

## How It Works

1. Input — Upload an audio/video file or record from your microphone
2. Transcription — The audio is sent to OpenAI Whisper, which converts speech to text
3. Extraction — The transcript is sent to Claude with a prompt asking it to identify tasks, owners, and deadlines
4. Display — Tasks are shown as interactive cards you can check off, with options to export

---

## Future Ideas

- Push tasks directly to Notion or Todoist
- Speaker detection to identify who said what
- Email summary after each meeting
- Deploy to Streamlit Cloud for access anywhere

---

## Acknowledgements

Built with OpenAI Whisper and Anthropic Claude.
