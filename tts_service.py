import os
import re
from datetime import datetime
from typing import Optional
from gtts import gTTS


def clean_llm_output(text: str) -> str:
    cleaned = re.sub(r'\([^)]*\)', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def generate_unique_filename(base_name: str = "generated_audio", extension: str = ".mp3") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"


def generate_audio(text: str, output_path: str) -> str:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    cleaned_text = clean_llm_output(text)

    if not output_path or not output_path.strip():
        raise ValueError("Output path cannot be empty")

    try:
        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # 🔥 Use gTTS (stable for Colab)
        tts = gTTS(text=cleaned_text, lang='en')
        tts.save(output_path)

        if not os.path.exists(output_path):
            raise Exception("Audio file was not created")

        return output_path

    except Exception as e:
        raise Exception(f"TTS failed: {str(e)}")


def generate_audio_with_voice(
    text: str,
    output_path: str,
    voice_id: Optional[int] = None,
    rate: int = 150,
    volume: float = 0.9
) -> str:
    # gTTS doesn't support voice/rate control → fallback
    return generate_audio(text, output_path)


def get_available_voices() -> list:
    # gTTS does not expose system voices
    return [{"id": 0, "name": "gTTS default (en)", "gender": "N/A", "languages": ["en"]}]
