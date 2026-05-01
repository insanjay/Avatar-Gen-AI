import whisper
import fitz
import os
import tempfile
from context_builder import build_context
from llm_service import generate_script
from tts_service import generate_audio
from video_service import generate_video
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"


# -------- PDF PROCESSING FUNCTION --------
def process_pdf(pdf_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(pdf_bytes)
        pdf_path = f.name

    doc = fitz.open(pdf_path)
    full_text = " ".join([page.get_text() for page in doc])
    doc.close()

    # ---- CHUNKING ----
    chunks = [full_text[i:i+1000] for i in range(0, len(full_text), 1000)]

    summaries = []

    for chunk in chunks[:5]:  # limit for speed + token safety
        summary = generate_script(
            f"Summarize this in 2 lines:\n{chunk}"
        )
        summaries.append(summary)

    final_summary = " ".join(summaries)

    return final_summary[:2000]


# -------- MAIN PIPELINE --------
def run_pipeline(text, pdf_bytes, audio_bytes, image_bytes):

    # -------- PDF --------
    pdf_text = process_pdf(pdf_bytes) if pdf_bytes else ""

    # -------- AUDIO (STT) --------
    audio_text = ""
    if audio_bytes:
        try:
            model = whisper.load_model("base")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio_bytes)
                audio_path = f.name

            result = model.transcribe(audio_path)
            audio_text = result.get("text", "")
        except:
            audio_text = ""

    # -------- CONTEXT --------
    context = build_context(
        text=text,
        audio=audio_text,
        pdf=pdf_text,
        instruction=(
            "Generate a simple spoken sentence for a talking avatar. "
            "Use easy words. 10–12 words only. "
            "Avoid technical terms. Speak naturally."
        )
    )

    # -------- LLM --------
    script = generate_script(context)
    print("SCRIPT:", script)

    if not script or len(script.strip()) < 5:
        script = "Hello, this is a test video."

    script = script.strip()[:150]

    # -------- TTS --------
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    audio_path = OUTPUT_DIR / "pipeline_audio.wav"
    audio_path = generate_audio(script, str(audio_path))

    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        raise Exception("Audio generation failed")

    # -------- IMAGE --------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(image_bytes)
        image_path = os.path.abspath(tmp.name)

    # -------- VIDEO --------
    video_path = generate_video(audio_path, image_path)

    return video_path


#  %cd /content/Avatar-Gen-AI