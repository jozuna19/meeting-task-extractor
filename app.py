import os
import csv
import io
import tempfile
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# -----------------------------
# CONFIG / KEYS (local + cloud)
# -----------------------------
load_dotenv()  # local dev

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))

if not OPENAI_API_KEY or not ANTHROPIC_API_KEY:
    st.error(
        "Missing API keys. Add OPENAI_API_KEY and ANTHROPIC_API_KEY to Streamlit Secrets "
        "or to a local .env file."
    )
    st.stop()

openai_client = OpenAI(api_key=OPENAI_API_KEY)
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)


# -----------------------------
# TRANSCRIPTION
# -----------------------------
def transcribe_file(filepath: str) -> str:
    """
    Transcribe an audio/video file using OpenAI's Whisper API.

    Note: Whisper API supports these formats:
    flac, m4a, mp3, mp4, mpeg, mpga, oga, ogg, wav, webm
    """
    supported = [
        ".flac", ".m4a", ".mp3", ".mp4", ".mpeg",
        ".mpga", ".oga", ".ogg", ".wav", ".webm"
    ]
    ext = os.path.splitext(filepath)[1].lower()

    # If user uploads .caf or other unsupported format, we currently do not
    # convert on Streamlit Cloud because ffmpeg may not be available.
    if ext not in supported:
        raise ValueError(
            f"Unsupported file type: {ext}. Please upload one of: "
            f"{', '.join(supported)}"
        )

    with open(filepath, "rb") as audio_file:
        result = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return result.text


# -----------------------------
# TASK EXTRACTION
# -----------------------------
def extract_tasks(transcript: str) -> str:
    """
    Ask Claude to extract tasks in a strict, parseable format.
    """
    message = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are a helpful assistant that extracts action items from meeting transcripts.

Extract all tasks and action items from the transcript below.
Return them as blocks in this exact format for each task:

TASK: <what needs to be done>
WHO: <person responsible, or 'Unassigned' if unknown>
DEADLINE: <deadline or timeframe, or 'Not specified' if unknown>
---

Only return the tasks in this format, nothing else.
If there are no tasks, return exactly: NO_TASKS

Transcript:
{transcript}"""
            }
        ]
    )
    return message.content[0].text


def parse_tasks(raw: str) -> list[dict]:
    """
    Parse Claude's structured output into:
    [{"what": "...", "who": "...", "deadline": "..."}, ...]
    """
    raw = (raw or "").strip()
    if raw == "NO_TASKS":
        return []

    tasks = []
    blocks = raw.split("---")
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        task = {"what": "", "who": "Unassigned", "deadline": "Not specified"}
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("TASK:"):
                task["what"] = line.replace("TASK:", "", 1).strip()
            elif line.startswith("WHO:"):
                task["who"] = line.replace("WHO:", "", 1).strip() or "Unassigned"
            elif line.startswith("DEADLINE:"):
                task["deadline"] = line.replace("DEADLINE:", "", 1).strip() or "Not specified"

        if task["what"]:
            tasks.append(task)

    return tasks


# -----------------------------
# EXPORT HELPERS
# -----------------------------
def tasks_to_csv(tasks: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["what", "who", "deadline"])
    writer.writeheader()
    for t in tasks:
        writer.writerow(
            {
                "what": t.get("what", ""),
                "who": t.get("who", ""),
                "deadline": t.get("deadline", ""),
            }
        )
    return output.getvalue()


def tasks_to_txt(tasks: list[dict]) -> str:
    lines = ["EXTRACTED TASKS", "=" * 40]
    for i, t in enumerate(tasks, 1):
        lines.append("")
        lines.append(f"Task {i}")
        lines.append(f"  What:     {t.get('what', '')}")
        lines.append(f"  Who:      {t.get('who', '')}")
        lines.append(f"  Deadline: {t.get('deadline', '')}")
    return "\n".join(lines)


# -----------------------------
# UI / STYLING
# -----------------------------
st.set_page_config(page_title="Meeting Task Extractor", page_icon="🎙️", layout="centered")

st.markdown(
    """
<style>
    .stApp { background-color: #0f1117; }

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

    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        margin: 1.5rem 0 0.8rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #2e3148;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">🎙️ Meeting Task Extractor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">Upload a recording to automatically extract tasks from any meeting or call.</div>',
    unsafe_allow_html=True,
)
st.divider()


def display_results(transcript: str, tasks: list[dict]):
    st.markdown('<div class="section-header">📝 Transcript</div>', unsafe_allow_html=True)
    with st.expander("Click to view full transcript"):
        st.write(transcript)

    if not tasks:
        st.info("No tasks or action items were found in this recording.")
        return

    st.markdown(
        f'<div class="section-header">✅ Extracted Tasks '
        f'<span style="color:#8b8fa8;font-size:0.9rem;">({len(tasks)} found)</span></div>',
        unsafe_allow_html=True,
    )

    for i, task in enumerate(tasks):
        col1, col2 = st.columns([0.08, 0.92])
        with col1:
            done = st.checkbox("Done", key=f"task_{i}", label_visibility="hidden")
        with col2:
            style = "opacity:0.45;text-decoration:line-through;" if done else ""
            st.markdown(
                f"""
                <div class="task-card" style="{style}">
                    <div class="task-title">{task.get('what', '')}</div>
                    <div class="task-meta">
                        <span class="badge badge-who">👤 {task.get('who', 'Unassigned')}</span>
                        <span class="badge badge-deadline">🗓 {task.get('deadline', 'Not specified')}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown('<div class="section-header">📤 Export</div>', unsafe_allow_html=True)
    colA, colB = st.columns(2)
    with colA:
        st.download_button(
            label="⬇️ Download as CSV",
            data=tasks_to_csv(tasks),
            file_name="tasks.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with colB:
        st.download_button(
            label="⬇️ Download as TXT",
            data=tasks_to_txt(tasks),
            file_name="tasks.txt",
            mime="text/plain",
            use_container_width=True,
        )


# -----------------------------
# MAIN: FILE UPLOAD ONLY
# -----------------------------
st.subheader("📁 Upload File")

uploaded_file = st.file_uploader(
    "Upload your audio or video file",
    type=["mp3", "mp4", "wav", "m4a", "ogg", "webm", "flac", "mpeg", "mpga", "oga"],
    help="For Streamlit Cloud, upload a supported format (mp3, wav, m4a, mp4, etc.).",
)

if uploaded_file:
    st.audio(uploaded_file)

    if st.button("Extract Tasks", type="primary"):
        suffix = os.path.splitext(uploaded_file.name)[1] or ".mp3"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            with st.spinner("🎙️ Transcribing audio..."):
                transcript = transcribe_file(tmp_path)

            with st.spinner("🤖 Extracting tasks..."):
                raw = extract_tasks(transcript)
                tasks = parse_tasks(raw)

            display_results(transcript, tasks)

        except ValueError as e:
            st.error(str(e))
        finally:
            # Best effort cleanup
            try:
                os.remove(tmp_path)
            except Exception:
                pass
