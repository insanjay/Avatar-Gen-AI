"""
Text-to-Speech Service Module for Modular AI Backend

This module provides TTS functionality using pyttsx3 to convert text input
into speech audio files. It handles text validation, audio generation,
and file saving operations.
"""

import os
import re
import time
from datetime import datetime
import pyttsx3
from typing import Optional


def clean_llm_output(text: str) -> str:
    """
    Clean LLM output by removing text inside parentheses.
    
    Args:
        text (str): Raw LLM output text
        
    Returns:
        str: Cleaned text with parenthetical content removed
    """
    # Remove text inside parentheses (including the parentheses)
    cleaned = re.sub(r'\([^)]*\)', '', text)
    # Clean up extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def generate_unique_filename(base_name: str = "generated_audio", extension: str = ".wav") -> str:
    """
    Generate a unique filename using timestamp.
    
    Args:
        base_name (str): Base name for the file
        extension (str): File extension
        
    Returns:
        str: Unique filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"


def generate_audio(text: str, output_path: str) -> str:
    """
    Convert text to speech and save as a .wav file.
    
    This function takes input text, converts it to speech using pyttsx3,
    and saves the result as a .wav audio file at the specified path.
    
    Args:
        text (str): The text to convert to speech
        output_path (str): The file path where the audio will be saved
        
    Returns:
        str: The path to the generated audio file
        
    Raises:
        ValueError: If text is empty or None
        ValueError: If output_path is empty or None
        Exception: If TTS engine fails or file saving fails
        
    Example:
        >>> audio_path = generate_audio("Hello world", "output.wav")
        >>> print(f"Audio saved to: {audio_path}")
    """
    
    # Validate input text
    if not text or not text.strip():
        raise ValueError("Text cannot be empty or None")
    
    # Clean LLM output by removing parenthetical content
    cleaned_text = clean_llm_output(text)
    
    # Validate output path
    if not output_path or not output_path.strip():
        raise ValueError("Output path cannot be empty or None")
    
    try:
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Configure voice properties
        engine.setProperty('rate', 150)    # Speech rate (words per minute)
        engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Save speech to file
        engine.save_to_file(cleaned_text, output_path)
        engine.runAndWait()
        
        # Verify file was created
        if not os.path.exists(output_path):
            raise Exception("Audio file was not created successfully")
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to generate audio: {str(e)}")


def generate_audio_with_voice(text: str, output_path: str, voice_id: Optional[int] = None, 
                            rate: int = 150, volume: float = 0.9) -> str:
    """
    Convert text to speech with customizable voice settings.
    
    This is an extended version that allows voice selection and
    custom speech parameters.
    
    Args:
        text (str): The text to convert to speech
        output_path (str): The file path where the audio will be saved
        voice_id (Optional[int]): Specific voice ID to use
        rate (int): Speech rate (words per minute)
        volume (float): Volume level (0.0 to 1.0)
        
    Returns:
        str: The path to the generated audio file
    """
    
    # Validate input text
    if not text or not text.strip():
        raise ValueError("Text cannot be empty or None")
    
    # Validate output path
    if not output_path or not output_path.strip():
        raise ValueError("Output path cannot be empty or None")
    
    try:
        # Initialize TTS engine
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        
        # Set voice if specified
        if voice_id is not None and 0 <= voice_id < len(voices):
            engine.setProperty('voice', voices[voice_id].id)
        
        # Configure voice properties
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        # Save speech to file
        engine.save_to_file(cleaned_text, output_path)
        engine.runAndWait()
        
        # Verify file was created
        if not os.path.exists(output_path):
            raise Exception("Audio file was not created successfully")
        
        return output_path
        
    except Exception as e:
        raise Exception(f"Failed to generate audio: {str(e)}")


def get_available_voices() -> list:
    """
    Get list of available TTS voices.
    
    Returns:
        list: List of voice information dictionaries
    """
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        voice_list = []
        for i, voice in enumerate(voices):
            voice_info = {
                'id': i,
                'name': voice.name,
                'gender': voice.gender,
                'languages': voice.languages
            }
            voice_list.append(voice_info)
        
        return voice_list
        
    except Exception as e:
        raise Exception(f"Failed to get available voices: {str(e)}")


if __name__ == "__main__":
    # Test the TTS service with LLM integration
    try:
        from llm_service import generate_script
        from context_builder import build_context
        
        # Build test context
        test_context = build_context(
            text="Artificial intelligence is transforming how we interact with technology.",
            audio="",
            pdf="Machine learning algorithms enable computers to learn from data and make predictions.",
            instruction="Generate a brief, engaging script about AI and machine learning."
        )
        
        print("----- BUILT CONTEXT -----")
        print(test_context)
        print("\n" + "="*50 + "\n")
        
        print("----- GENERATING LLM RESPONSE -----")
        llm_response = generate_script(test_context)
        print(f"LLM Response: {llm_response}")
        print("\n" + "="*50 + "\n")
        
        print("----- GENERATING AUDIO -----")
        output_file = generate_unique_filename()
        audio_path = generate_audio(llm_response, output_file)
        print(f"Audio generated successfully: {audio_path}")
        
        # Display available voices
        print("\n----- AVAILABLE VOICES -----")
        voices = get_available_voices()
        for voice in voices:
            print(f"ID {voice['id']}: {voice['name']} ({voice['gender']})")
        
    except ValueError as e:
        print(f"Validation Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure pyttsx3 is installed:")
        print("pip install pyttsx3")
