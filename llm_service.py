"""
Groq LLM Service Module for Modular AI Backend

This module provides integration with Groq's API for generating text responses
using chat completion models. It handles authentication, context validation,
and response processing.
"""

import os
from dotenv import load_dotenv
from groq import Groq
from typing import Optional

# Load environment variables from .env file
load_dotenv()


def generate_script(context: str) -> str:
    """
    Generate text response using Groq's chat completion API.
    
    This function takes a context string and generates a response using
    Groq's LLM model. The context is used as the user message in the
    chat completion request.
    
    Args:
        context (str): The context string to send to the LLM
        
    Returns:
        str: Generated text response from the LLM
        
    Raises:
        ValueError: If context is empty or None
        ValueError: If GROQ_API_KEY environment variable is not set
        Exception: If API call fails
        
    Example:
        >>> context = "Summarize this text about AI"
        >>> response = generate_script(context)
        >>> print(response)
    """
    
    # Validate context input
    if not context or not context.strip():
        raise ValueError("Context cannot be empty or None")
    
    # Get API key from environment variable
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    
    try:
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Create chat completion request
        chat_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Fast and efficient model
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI script generator. Carefully read all provided sections (TEXT INPUT, AUDIO TRANSCRIPTION, PDF CONTENT) and generate a clear, natural spoken script. Do not ignore any section if present."
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stream=False
        )
        
        # Extract and return the generated text
        response_text = chat_completion.choices[0].message.content
        return response_text.strip() if response_text else ""
        
    except Exception as e:
        raise Exception(f"Failed to generate response from Groq API: {str(e)}")


def generate_script_with_model(context: str, model: str = "llama-3.1-8b-instant") -> str:
    """
    Generate text response using a specific Groq model.
    
    This is an extended version that allows model selection.
    
    Args:
        context (str): The context string to send to the LLM
        model (str): The Groq model to use (default: llama-3.1-8b-instant)
        
    Returns:
        str: Generated text response from the LLM
    """
    
    # Validate context input
    if not context or not context.strip():
        raise ValueError("Context cannot be empty or None")
    
    # Get API key from environment variable
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    
    try:
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Create chat completion request
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI script generator. Convert the given context into a clear, engaging spoken script suitable for narration in a video. Keep it natural and well-structured."

                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            temperature=0.7,
            max_tokens=512,
            top_p=1,
            stream=False
        )
        
        # Extract and return the generated text
        response_text = chat_completion.choices[0].message.content
        print("LLM Response Generated Successfully")
        return response_text.strip() if response_text else ""
        
    except Exception as e:
        raise Exception(f"Failed to generate response from Groq API: {str(e)}")


if __name__ == "__main__":
    # Test the LLM service with context_builder integration
    try:
        from context_builder import build_context
        
        # Build test context
        test_context = build_context(
            text="This is a test text input for the LLM service.",
            audio="",
            pdf="This is test PDF content about artificial intelligence and machine learning.",
            instruction="Generate a brief summary of the provided content."
        )
        
        print("----- BUILT CONTEXT -----")
        print(test_context)
        print("\n" + "="*50 + "\n")
        
        print("----- LLM RESPONSE -----")
        response = generate_script(test_context)
        print(response)
        
    except ValueError as e:
        print(f"Validation Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure to set the GROQ_API_KEY environment variable:")
        print("export GROQ_API_KEY='your_api_key_here'")
