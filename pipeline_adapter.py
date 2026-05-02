import os
import tempfile

from context_builder import build_context
from llm_service import generate_script
from tts_service import generate_audio
from video_service import generate_video


def run_pipeline(
    text=None,
    pdf_bytes=None,
    audio_bytes=None,
    image_bytes=None
):
    # ---------- VALIDATION ----------
    if not any([text, pdf_bytes, audio_bytes]):
        raise ValueError("At least one input (text/pdf/audio) is required")

    if image_bytes is None:
        raise ValueError("Avatar image is required")

    # ---------- TEXT INPUT ----------
    text_input = text.strip() if text else ""

    # ---------- PDF PROCESSING ----------
    pdf_text = ""
    if pdf_bytes:
        try:
            pdf_text = pdf_bytes.decode(errors="ignore")
        except:
            pdf_text = ""

    # ---------- AUDIO PROCESSING ----------
    audio_text = ""
    if audio_bytes:
        # placeholder (replace later with Whisper if needed)
        audio_text = "Audio input provided"

    # ---------- CONTEXT BUILD ----------
    context = build_context(
        text=text_input,
        audio=audio_text,
        pdf=pdf_text,
        instruction="Generate a short 5-second script (10–15 words)"
    )

    # ---------- LLM ----------
    script = generate_script(context)

    if not script or len(script.strip()) < 5:
        script = "Hello, this is a test video."

    script = script.strip()[:150]

    print("SCRIPT:", script)

    # ---------- TTS ----------
    audio_path = os.path.abspath("pipeline_audio.mp3")
    audio_path = generate_audio(script, audio_path)

    if not os.path.exists(audio_path):
        raise Exception("Audio generation failed")

    # ---------- IMAGE SAVE ----------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        tmp.write(image_bytes)
        image_path = os.path.abspath(tmp.name)

    # ---------- VIDEO ----------
    video_path = generate_video(audio_path, image_path)

    return video_path
