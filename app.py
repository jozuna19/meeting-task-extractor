import os
import re
import tempfile
import streamlit as st
import sounddevice as sd
from scipy.io.wavfile import write
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
import csv
import io

# Load API keys
load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# --- TRANSCRIPTION ---

def transcribe_file(filepath):
    supported = ['.flac', '.m4a', '.mp3', '.mp4', '.mpeg', '.mpga', '.oga', '.ogg', '.wav', '.webm']
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in supported:
        converted = filepath.replace(ext, "_converted.mp3")
        os.system(f'ffmpeg -i "{filepath}" "{converted}" -y -loglevel quiet')
        filepath = converted
    with open(filepath, "rb") as audio_file:
        result = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return result.text


def record_and_transcribe(duration=60):
    sample_rate = 44100
    with st.spinner(f"🎤 Recording for {duration} seconds..."):
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        write(tmp.name, sample_rate, audio)
        return transcribe_file(tmp.name)


# --- TASK EXTRACTION ---

def extract_tasks(transcript):
    message = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are a helpful assistant that extracts action items from meeting transcripts.

Extract all tasks and action items from the transcript below.
Return them as a numbered list in this exact format for each task:

TASK: <what needs to be done>
WHO: <person responsible, or 'Unassigned' if unknown>
DEADLINE: <deadline or timeframe, or 'Not specified' if unknown>
---

Only return the tasks in this format, nothing else.

Transcript:
{transcript}"""
            }
        ]
    )
    return message.content[0].text


def parse_tasks(raw):
    """Parse Claude's structured output into a list of task dicts."""
    tasks = []
    blocks = raw.strip().split("---")
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        task = {}
        for line in block.splitlines():
            if line.startswith("TASK:"):
                task["what"] = line.replace("TASK:", "").strip()
            elif line.startswith("WHO:"):
                task["who"] = line.replace("WHO:", "").strip()
            elif line.startswith("DEADLINE:"):
                task["deadline"] = line.replace("DEADLINE:", "").strip()
        if "what" in task:
            tasks.append(task)
    return tasks


def tasks_to_csv(tasks):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["what", "who", "deadline"])
    writer.writeheader()
    for t in tasks:
        writer.writerow({"what": t.get("what", ""), "who": t.get("who", ""), "deadline": t.get("deadline", "")})
    return output.getvalue()


def tasks_to_txt(tasks):
    lines = ["EXTRACTED TASKS\n" + "=" * 40]
    for i, t in enumerate(tasks, 1):
        lines.append(f"\nTask {i}")
        lines.append(f"  What:     {t.get('what', '')}")
        lines.append(f"  Who:      {t.get('who', '')}")
        lines.append(f"  Deadline: {t.get('deadline', '')}")
    return "\n".join(lines)


# --- PAGE CONFIG ---

st.set_page_config(page_title="Meeting Task Extractor", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
    /* Background */
    .stApp { background-color: #0f1117; }

    /* Title */
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0.2rem;
    }
    .main-subtitle {
        color: #8b8fa8;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }

    /* Task cards */
    .task-card {
        background: #1c1e2e;
        border: 1px solid #2e3148;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .task-title {
        font-size: 1rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.4rem;
    }
    .task-meta {
        font-size: 0.82rem;
        color: #8b8fa8;
    }
    .task-meta span {
        margin-right: 1.2rem;
    }
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .badge-who { background: #1e3a5f; color: #60a5fa; }
    .badge-deadline { background: #2d1f4e; color: #a78bfa; }

    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #2e3148;
    }

    /* Export buttons row */
    .export-row {
        display: flex;
        gap: 0.8rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# --- HEADER ---
st.markdown('<div class="main-title">🎙️ Meeting Task Extractor</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Upload a recording or use your microphone to automatically extract tasks from any meeting or call.</div>', unsafe_allow_html=True)
st.divider()


# --- PROCESS & DISPLAY ---

def display_results(transcript, tasks):
    # Transcript expander
    st.markdown('<div class="section-header">📝 Transcript</div>', unsafe_allow_html=True)
    with st.expander("Click to view full transcript"):
        st.write(transcript)

    if not tasks:
        st.info("No tasks or action items were found in this recording.")
        return

    # Task count
    st.markdown(f'<div class="section-header">✅ Extracted Tasks &nbsp;<span style="color:#8b8fa8;font-size:0.9rem;">({len(tasks)} found)</span></div>', unsafe_allow_html=True)

    # Checkboxes + cards
    completed = []
    for i, task in enumerate(tasks):
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            done = st.checkbox("", key=f"task_{i}")
            completed.append(done)
        with col2:
            style = "opacity:0.45;text-decoration:line-through;" if done else ""
            st.markdown(f"""
            <div class="task-card" style="{style}">
                <div class="task-title">{task.get('what', '')}</div>
                <div class="task-meta">
                    <span class="badge badge-who">👤 {task.get('who', 'Unassigned')}</span>
                    <span class="badge badge-deadline">🗓 {task.get('deadline', 'Not specified')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Export
    st.markdown('<div class="section-header">📤 Export</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Download as CSV",
            data=tasks_to_csv(tasks),
            file_name="tasks.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col2:
        st.download_button(
            label="⬇️ Download as TXT",
            data=tasks_to_txt(tasks),
            file_name="tasks.txt",
            mime="text/plain",
            use_container_width=True
        )


# --- TABS ---
tab1, tab2 = st.tabs(["📁 Upload File", "🎤 Record Microphone"])

with tab1:
    uploaded_file = st.file_uploader(
        "Upload your audio or video file",
        type=["mp3", "mp4", "wav", "m4a", "ogg", "webm", "flac", "caf", "mpeg"]
    )
    if uploaded_file:
        st.audio(uploaded_file)
        if st.button("Extract Tasks", key="file_btn", type="primary"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name
            with st.spinner("🎙️ Transcribing audio..."):
                transcript = transcribe_file(tmp_path)
            with st.spinner("🤖 Extracting tasks..."):
                raw = extract_tasks(transcript)
                tasks = parse_tasks(raw)
            display_results(transcript, tasks)

with tab2:
    duration = st.slider("Recording duration (seconds)", min_value=10, max_value=300, value=60, step=10)
    if st.button("Start Recording", key="mic_btn", type="primary"):
        transcript = record_and_transcribe(duration)
        with st.spinner("🤖 Extracting tasks..."):
            raw = extract_tasks(transcript)
            tasks = parse_tasks(raw)
        display_results(transcript, tasks)