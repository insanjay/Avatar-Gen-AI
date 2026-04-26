"""
Context Builder Module for Modular AI Backend

This module provides functionality to combine multiple input sources (text, audio transcription, 
and PDF processed text) into a single formatted context string suitable for LLM prompts.
"""

def build_context(text: str, audio: str, pdf: str, instruction: str) -> str:
    """
    Build a comprehensive context string from multiple input sources.
    """

    if not any([
        text and text.strip(),
        audio and audio.strip(),
        pdf and pdf.strip()
    ]):
        raise ValueError("At least one input (text, audio, pdf) is required.")

    context_sections = []

    if instruction and instruction.strip():
        context_sections.append(f"INSTRUCTION:\n{instruction.strip()}")

    if text and text.strip():
        context_sections.append(f"TEXT INPUT:\n{text.strip()}")

    if audio and audio.strip():
        context_sections.append(f"AUDIO TRANSCRIPTION:\n{audio.strip()}")

    if pdf and pdf.strip():
        context_sections.append(f"PDF CONTENT:\n{pdf.strip()}")

    return "\n\n".join(context_sections)

def build_context_with_metadata(text: str, audio: str, pdf: str, instruction: str) -> dict:
    """
    Build context along with metadata about which sources were used.
    
    This is an extended version that returns both the formatted context and
    metadata about which input sources contributed to the final context.
    
    Args:
        text (str): Direct text input from user
        audio (str): Transcribed audio content as string
        pdf (str): Processed PDF content as string
        instruction (str): Additional instructions or context for the LLM
        
    Returns:
        dict: Dictionary containing 'context' and 'sources_used' keys
    """
    sources_used = []
    
    if instruction and instruction.strip():
        sources_used.append("instruction")
    if text and text.strip():
        sources_used.append("text")
    if audio and audio.strip():
        sources_used.append("audio")
    if pdf and pdf.strip():
        sources_used.append("pdf")
    
    context = build_context(text, audio, pdf, instruction)
    
    return {
        "context": context,
        "sources_used": sources_used,
        "total_sources": len(sources_used)
    }


if __name__ == "__main__":
    result = build_context(
        text="This is direct text input",
        audio="This is audio transcription",
        pdf="This is extracted PDF content",
        instruction="Summarize the combined input"
    )

    print("----- CONTEXT OUTPUT -----")
    print(result)

    print("\n----- WITH METADATA -----")
    meta = build_context_with_metadata(
        text="This is direct text input",
        audio="",
        pdf="PDF content here",
        instruction="Explain briefly"
    )
    print(meta)