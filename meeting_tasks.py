import os
import tempfile
import sounddevice as sd
from scipy.io.wavfile import write
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

# Load your API keys from .env
load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# --- STEP 1: TRANSCRIPTION ---

def transcribe_file(filepath):
    """Transcribe an audio/video file using Whisper."""
    print(f"\n🎙️  Transcribing file: {filepath}")
    with open(filepath, "rb") as audio_file:
        result = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return result.text


def record_and_transcribe(duration=60):
    """Record from microphone and transcribe."""
    sample_rate = 44100
    print(f"\n🎤 Recording for {duration} seconds... Press Ctrl+C to stop early.")
    
    try:
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
    except KeyboardInterrupt:
        print("\n⏹️  Recording stopped early.")
    
    # Save to a temporary file and transcribe
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        write(tmp.name, sample_rate, audio)
        return transcribe_file(tmp.name)


# --- STEP 2: TASK EXTRACTION ---

def extract_tasks(transcript):
    """Send transcript to Claude and extract tasks."""
    print("\n🤖 Extracting tasks from transcript...")
    
    message = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are a helpful assistant that extracts action items and tasks from meeting transcripts.

Please review the following transcript and extract all tasks, action items, or to-dos mentioned.
For each task, identify:
- What needs to be done
- Who is responsible (if mentioned)
- Any deadline or timeframe (if mentioned)

Format each task clearly and numbered. If no tasks are found, say so.

Transcript:
{transcript}"""
            }
        ]
    )
    return message.content[0].text


# --- STEP 3: MAIN MENU ---

def main():
    print("=" * 50)
    print("       MEETING TASK EXTRACTOR")
    print("=" * 50)
    print("\nHow would you like to input your meeting?")
    print("  1. Upload an audio/video file (MP3, MP4, etc.)")
    print("  2. Record from microphone")
    print("\nEnter 1 or 2: ", end="")
    
    choice = input().strip()
    
    if choice == "1":
        print("\nEnter the full path to your file: ", end="")
        filepath = input().strip()
        if not os.path.exists(filepath):
            print("❌ File not found. Please check the path and try again.")
            return
        transcript = transcribe_file(filepath)
    
    elif choice == "2":
        print("\nHow many seconds do you want to record? (default 60): ", end="")
        duration_input = input().strip()
        duration = int(duration_input) if duration_input.isdigit() else 60
        transcript = record_and_transcribe(duration)
    
    else:
        print("❌ Invalid choice.")
        return
    
    # Show transcript
    print("\n--- TRANSCRIPT ---")
    print(transcript)
    
    # Extract and show tasks
    tasks = extract_tasks(transcript)
    print("\n--- EXTRACTED TASKS ---")
    print(tasks)
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()