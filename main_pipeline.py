"""
Main AI Pipeline Module

This module orchestrates the complete AI pipeline from input text/audio/PDF
to final talking head video generation. It connects all modules:
context_builder -> llm_service -> tts_service -> video_service
"""

import os
from typing import Optional
import time

# Import all service modules
from context_builder import build_context
from llm_service import generate_script
from tts_service import generate_audio, clean_llm_output
from video_service import generate_video

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "outputs"
SADTALKER_EXAMPLES_DIR = PROJECT_ROOT / "SadTalker" / "examples"


def generate_full_video(text: str, audio: str, pdf: str, image_path: str, 
                       instruction: str = "Generate a 20–30 second spoken script (60–100 words), concise and clear.") -> str:
    """
    Generate a complete talking head video from multiple input sources.
    
    This function orchestrates the full AI pipeline:
    1. Build context from text, audio, and PDF inputs
    2. Generate script using LLM
    3. Convert script to audio using TTS
    4. Generate talking head video using SadTalker
    
    Args:
        text (str): Direct text input
        audio (str): Audio transcription string
        pdf (str): PDF processed text string
        image_path (str): Path to source image for video generation
        instruction (str): Instruction for LLM script generation
        
    Returns:
        str: Path to the generated video file
        
    Raises:
        ValueError: If required inputs are missing or invalid
        FileNotFoundError: If image_path doesn't exist
        Exception: If any pipeline step fails
        
    Example:
        >>> video_path = generate_full_video(
        ...     text="AI is transforming technology",
        ...     audio="",
        ...     pdf="Machine learning enables automation",
        ...     image_path="person.jpg"
        ... )
        >>> print(f"Generated video: {video_path}")
    """
    
    print("=== STARTING AI PIPELINE ===")
    
    # Step 1: Validate inputs
    print("\n[STEP 1/4] Validating inputs...")
    
    if not image_path or not image_path.strip():
        raise ValueError("Image path is required for video generation")
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Check if at least one content source is provided
    if not any([text and text.strip(), audio and audio.strip(), pdf and pdf.strip()]):
        raise ValueError("At least one input (text, audio, pdf) must be provided")
    
    print(f"  - Image path: {image_path}")
    print(f"  - Text input: {'Provided' if text and text.strip() else 'None'}")
    print(f"  - Audio input: {'Provided' if audio and audio.strip() else 'None'}")
    print(f"  - PDF input: {'Provided' if pdf and pdf.strip() else 'None'}")
    print("  - All inputs validated successfully")
    
    # Step 2: Build context
    print("\n[STEP 2/4] Building context from inputs...")
    
    try:
        context = build_context(text, audio, pdf, instruction)
        print("  - Context built successfully")
        print(f"  - Context length: {len(context)} characters")
    except Exception as e:
        raise Exception(f"Failed to build context: {str(e)}")
    
    # Step 3: Generate script using LLM
    print("\n[STEP 3/4] Generating script with LLM...")
    
    try:
        script = generate_script(context)
        print("  - Script generated successfully")
        print(f"  - Script length: {len(script)} characters")
        # Safe script preview - avoid slicing errors
        preview = script[:100] + "..." if len(script) > 100 else script
        print(f"  - Script preview: {preview}")
    except Exception as e:
        raise Exception(f"Failed to generate script: {str(e)}")
    
    # Step 4: Convert script to audio
    print("\n[STEP 4/4] Converting script to audio...")
    
    try:
        # Clean LLM output before TTS
        cleaned_script = clean_llm_output(script)
        print(f"  - Script cleaned for TTS")
        
        # Generate unique audio filename
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        audio_filename = OUTPUT_DIR / f"pipeline_audio_{int(time.time())}.wav"
        audio_path = generate_audio(cleaned_script, str(audio_filename))


        print(f"  - Audio generated: {audio_path}")
    except Exception as e:
        raise Exception(f"Failed to generate audio: {str(e)}")
    
    # Step 5: Generate video
    print("\n[STEP 5/5] Generating talking head video...")
    
    try:
        video_path = generate_video(audio_path, image_path)
        print(f"  - Video generated: {video_path}")
    except Exception as e:
        raise Exception(f"Failed to generate video: {str(e)}")
    
    print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")
    print(f"Final video: {video_path}")
    
    return video_path


def generate_full_video_with_config(text: str, audio: str, pdf: str, image_path: str,
                                   instruction: str = "Generate a clear, engaging script for a talking head video.",
                                   audio_filename: Optional[str] = None,
                                   cleanup_temp: bool = True) -> dict:
    """
    Generate video with additional configuration options.
    
    This is an extended version that provides more control over the pipeline
    and returns detailed information about the process.
    
    Args:
        text (str): Direct text input
        audio (str): Audio transcription string
        pdf (str): PDF processed text string
        image_path (str): Path to source image
        instruction (str): Instruction for LLM script generation
        audio_filename (Optional[str]): Custom audio filename
        cleanup_temp (bool): Whether to clean up temporary files
        
    Returns:
        dict: Dictionary containing video_path and pipeline metadata
    """
    
    import time
    from datetime import datetime
    
    pipeline_start = time.time()
    
    print("=== STARTING AI PIPELINE (CONFIGURABLE) ===")
    
    # Track pipeline steps
    pipeline_info = {
        "start_time": datetime.now().isoformat(),
        "steps_completed": [],
        "files_created": [],
        "errors": []
    }
    
    try:
        # Step 1: Validate inputs
        print("\n[STEP 1/5] Validating inputs...")
        
        if not image_path or not image_path.strip():
            raise ValueError("Image path is required for video generation")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if not any([text and text.strip(), audio and audio.strip(), pdf and pdf.strip()]):
            raise ValueError("At least one input (text, audio, pdf) must be provided")
        
        pipeline_info["steps_completed"].append("input_validation")
        print("  - Inputs validated successfully")
        
        # Step 2: Build context
        print("\n[STEP 2/5] Building context...")
        
        try:
            context = build_context(text, audio, pdf, instruction)
            pipeline_info["steps_completed"].append("context_building")
            pipeline_info["context_length"] = len(context)
            print(f"  - Context built ({len(context)} chars)")
        except Exception as e:
            pipeline_info["errors"].append(f"Context building: {str(e)}")
            raise Exception(f"Failed to build context: {str(e)}")
        
        # Step 3: Generate script
        print("\n[STEP 3/5] Generating script...")
        
        try:
            script = generate_script(context)
            pipeline_info["steps_completed"].append("script_generation")
            pipeline_info["script_length"] = len(script)
            pipeline_info["script_preview"] = script[:100] + "..." if len(script) > 100 else script
            print(f"  - Script generated ({len(script)} chars)")
        except Exception as e:
            pipeline_info["errors"].append(f"Script generation: {str(e)}")
            raise Exception(f"Failed to generate script: {str(e)}")
        
        # Step 4: Generate audio
        print("\n[STEP 4/5] Generating audio...")
        
        try:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            if audio_filename is None:
                timestamp = int(time.time())
                audio_filename = OUTPUT_DIR / f"pipeline_audio_{timestamp}.wav"
            
            cleaned_script = clean_llm_output(script)
            audio_path = generate_audio(cleaned_script, str(audio_filename))
            pipeline_info["steps_completed"].append("audio_generation")
            pipeline_info["files_created"].append(audio_path)
            print(f"  - Audio generated: {audio_path}")
        except Exception as e:
            pipeline_info["errors"].append(f"Audio generation: {str(e)}")
            raise Exception(f"Failed to generate audio: {str(e)}")
        
        # Step 5: Generate video
        print("\n[STEP 5/5] Generating video...")
        
        try:
            video_path = generate_video(audio_path, image_path)
            pipeline_info["steps_completed"].append("video_generation")
            pipeline_info["files_created"].append(video_path)
            print(f"  - Video generated: {video_path}")
        except Exception as e:
            pipeline_info["errors"].append(f"Video generation: {str(e)}")
            raise Exception(f"Failed to generate video: {str(e)}")
        
        # Calculate pipeline duration
        pipeline_end = time.time()
        pipeline_info["end_time"] = datetime.now().isoformat()
        pipeline_info["duration_seconds"] = pipeline_end - pipeline_start
        pipeline_info["video_path"] = video_path
        pipeline_info["success"] = True
        
        print("\n=== PIPELINE COMPLETED SUCCESSFULLY ===")
        print(f"Duration: {pipeline_info['duration_seconds']:.2f} seconds")
        print(f"Final video: {video_path}")
        
        return pipeline_info
        
    except Exception as e:
        pipeline_info["end_time"] = datetime.now().isoformat()
        pipeline_info["success"] = False
        pipeline_info["final_error"] = str(e)
        
        print(f"\n=== PIPELINE FAILED ===")
        print(f"Error: {str(e)}")
        
        return pipeline_info


if __name__ == "__main__":
    # Test the complete pipeline
    try:
        print("=== TESTING AI PIPELINE ===")
        
        # Example inputs
        test_text = "Artificial intelligence is revolutionizing how we interact with technology."
        test_audio = "Machine learning algorithms enable computers to learn from data and make intelligent decisions."
        test_pdf = "Deep learning neural networks have transformed fields like computer vision and natural language processing."
        test_image = ostr(SADTALKER_EXAMPLES_DIR / "source_image" / "full_body_1.png")
        
        # Check if test image exists
        if not os.path.exists(test_image):
            print(f"Warning: Test image {test_image} not found.")
            print("Please provide a valid image path to test the pipeline.")
            print("Example: python main_pipeline.py")
            exit(1)
        
        # Run pipeline
        video_path = generate_full_video(
            text=test_text,
            audio=test_audio,
            pdf=test_pdf,
            image_path=test_image,
            instruction="Create a comprehensive explanation of AI technologies for a general audience."
        )
        
        print(f"\nPipeline test completed successfully!")
        print(f"Generated video: {video_path}")
        
    except Exception as e:
        print(f"Pipeline test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure all modules are in the same directory")
        print("2. Check that SadTalker is properly installed and configured")
        print("3. Verify that the source image exists")
        print("4. Ensure GROQ_API_KEY is set in .env file")
