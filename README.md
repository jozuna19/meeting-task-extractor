🎙 Meeting Task Extractor

Transcribe meetings into structured action items — automatically.

AI-powered web application that converts meeting recordings into clear, actionable task lists with owners and deadlines.

Built with Python, Streamlit, OpenAI Whisper, and Anthropic Claude.

✨ What It Does

Upload a meeting recording and the app will:

🎧 Transcribe speech to text using Whisper

🧠 Extract action items using Claude

🗂 Identify:

What needs to be done

Who is responsible

Any deadlines or timeframes

✅ Display tasks as interactive checkable cards

📤 Export tasks as CSV or TXT

Turns messy conversations into structured execution.

🌐 Live Demo

Deployed on Streamlit Cloud.

Supported file formats:

mp3

m4a

wav

mp4

ogg

webm

flac

Note: Microphone recording is supported locally only.
The deployed cloud version uses file upload due to server-side hardware limitations.

🛠 Tech Stack

Backend

Python

Streamlit

AI Services

OpenAI Whisper API (speech-to-text)

Anthropic Claude API (task extraction)

Other

python-dotenv

Structured LLM prompting & response parsing

🧩 How It Works
Audio File → Whisper (Transcript) → Claude (Task Extraction) → Structured Tasks → Export

User uploads audio

File is temporarily stored server-side

Whisper generates a transcript

Claude extracts action items in a structured format

Output is parsed into task objects

Tasks are displayed and available for export

🖥 Local Development

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
🚀 Deployment

Deployed via Streamlit Cloud.

Secrets are stored securely using the Streamlit Secrets manager:

OPENAI_API_KEY = "your_openai_key"
ANTHROPIC_API_KEY = "your_anthropic_key"
📈 Why This Project Matters

This project demonstrates:

Multi-API integration

Real-world AI workflow design

Structured LLM prompting and parsing

Secure secrets management

Cloud deployment

Clean UI/UX implementation

It solves a real productivity problem by transforming unstructured speech into actionable outputs.

🔮 Future Improvements

Browser-based microphone recording

Speaker diarization (who said what)

Notion / Todoist integration

PDF export

Automated meeting summaries

Calendar follow-up generation
