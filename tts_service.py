import os
import re
from datetime import datetime
from gtts import gTTS
from typing import Optional


def clean_llm_output(text: str) -> str:
    """
    Remove unnecessary parenthetical content from LLM output.
    """

    cleaned = re.sub(r'\([^)]*\)', '', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned


def generate_unique_filename(
    base_name: str = "generated_audio",
    extension: str = ".mp3"
) -> str:

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    return f"{base_name}_{timestamp}{extension}"


def generate_audio(text: str, output_path: str) -> str:
    """
    Generate speech using gTTS.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if not output_path or not output_path.strip():
        raise ValueError("Output path cannot be empty")

    cleaned_text = clean_llm_output(text)

    try:

        output_dir = os.path.dirname(output_path)

        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Ensure mp3 extension
        if not output_path.endswith(".mp3"):
            output_path += ".mp3"

        tts = gTTS(
            text=cleaned_text,
            lang="en",
            slow=False
        )

        tts.save(output_path)

        if not os.path.exists(output_path):
            raise Exception("Audio file was not created")

        return output_path

    except Exception as e:
        raise Exception(f"Failed to generate audio: {str(e)}")


if __name__ == "__main__":

    sample_text = "Artificial Intelligence helps machines learn like humans."

    output_file = generate_unique_filename()

    path = generate_audio(sample_text, output_file)

    print("Generated:", path)