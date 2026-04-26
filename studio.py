"""
Streamlit Studio Page for AI Video Generation

This app provides a professional UI for generating talking head videos
using the existing backend pipeline with enhanced controls and user experience.
"""

import streamlit as st
import os
import tempfile
from main_pipeline import generate_full_video


def build_instruction(duration: str, tone: str) -> str:
    """Build dynamic instruction based on duration and tone."""
    duration_words = {
        "15s": "40–60 words",
        "30s": "80–120 words", 
        "60s": "150–200 words"
    }
    
    tone_instructions = {
        "Formal": "Generate a professional, formal spoken script",
        "Friendly": "Generate a friendly, conversational spoken script",
        "Casual": "Generate a casual, relaxed spoken script"
    }
    
    word_count = duration_words.get(duration, "80–120 words")
    tone_instruction = tone_instructions.get(tone, "Generate a clear, engaging spoken script")
    
    return f"{tone_instruction} ({word_count}), {duration} long."


def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary location and return path."""
    if uploaded_file is None:
        return None
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getbuffer())
        return tmp_file.name


def main():
    """Main Studio page function."""
    st.set_page_config(
        page_title="AI Video Studio",
        page_icon="🎬",
        layout="wide"
    )
    
    # Initialize session state
    if 'video_path' not in st.session_state:
        st.session_state.video_path = None
    if 'error_message' not in st.session_state:
        st.session_state.error_message = None
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    
    st.title("🎬 AI Video Studio")
    
    # Create 3-column layout
    left_col, center_col, right_col = st.columns([1, 2, 1])
    
    with left_col:
        st.header("📝 Inputs")
        
        # Text input
        text_input = st.text_area(
            "Script Content *",
            placeholder="Enter your script content here...",
            height=200,
            help="Main content for the video script"
        )
        
        # Image upload
        uploaded_image = st.file_uploader(
            "Source Image *",
            type=['jpg', 'jpeg', 'png'],
            help="Upload a clear front-facing photo for best results"
        )
        
        # PDF upload (optional)
        uploaded_pdf = st.file_uploader(
            "PDF Document",
            type=['pdf', 'txt'],
            help="Upload PDF or text file for additional content"
        )
        
        # Extract PDF content if uploaded
        pdf_content = ""
        if uploaded_pdf is not None:
            try:
                if uploaded_pdf.name.endswith('.pdf'):
                    import PyPDF2
                    import io
                    pdf_bytes = io.BytesIO(uploaded_pdf.read())
                    pdf_reader = PyPDF2.PdfReader(pdf_bytes)
                    pdf_content = "\n".join([page.extract_text() for page in pdf_reader.pages])
                else:
                    pdf_content = uploaded_pdf.read().decode('utf-8')
            except Exception as e:
                st.error(f"Failed to read PDF: {e}")
                pdf_content = ""
        
        # Display uploaded image preview
        if uploaded_image is not None:
            st.image(uploaded_image, caption="Uploaded Image", width=250)
    
    with center_col:
        st.header("⚙️ Settings")
        
        # Duration selector
        duration = st.selectbox(
            "Video Duration",
            options=["15s", "30s", "60s"],
            index=1,
            help="Target length for the generated script"
        )
        
        # Tone selector
        tone = st.selectbox(
            "Script Tone",
            options=["Formal", "Friendly", "Casual"],
            index=0,
            help="Style of the generated script"
        )
        
        # Warning about processing time
        st.warning("⏱️ Video generation may take several minutes depending on duration.")
    
    with right_col:
        st.header("📊 Status")
        
        # Processing status
        if st.session_state.is_processing:
            st.info("🔄 Processing video generation...")
        elif st.session_state.video_path:
            st.success("✅ Video generated successfully!")
        else:
            st.info("🎬 Ready to generate video")
        
        # Generate button
        generate_button = st.button(
            "🚀 Generate Video",
            type="primary",
            use_container_width=True,
            disabled=uploaded_image is None or 
                     not text_input.strip() or 
                     st.session_state.is_processing
        )
    
    # Error display
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        st.session_state.error_message = None
    
    # Generation logic
    if generate_button and uploaded_image is not None and not st.session_state.is_processing:
        # Validate inputs
        if not text_input.strip():
            st.session_state.error_message = "Script content is required."
            st.rerun()
            return
        
        # Set processing state
        st.session_state.is_processing = True
        st.session_state.video_path = None
        
        # Save uploaded image
        image_path = save_uploaded_file(uploaded_image)
        if image_path is None:
            st.session_state.error_message = "Failed to save uploaded image."
            st.session_state.is_processing = False
            st.rerun()
            return
        
        try:
            # Build dynamic instruction
            instruction = build_instruction(duration, tone)
            
            # Call pipeline with spinner
            with st.spinner("🎬 Generating video... This may take several minutes."):
                video_path = generate_full_video(
                    text=text_input,
                    audio="",
                    pdf=pdf_content,
                    image_path=image_path,
                    instruction=instruction
                )
            
            # Success
            st.session_state.video_path = video_path
            st.success("✅ Video generated successfully!")
            
        except Exception as e:
            st.session_state.error_message = f"Error: {str(e)}"
            st.session_state.video_path = None
        
        finally:
            # Reset processing state
            st.session_state.is_processing = False
            st.rerun()
    
    # Video output section
    if st.session_state.video_path and st.session_state.video_path:
        st.header("🎥 Generated Video")
        
        # Check if video file exists
        if os.path.exists(st.session_state.video_path):
            # Display video
            st.video(st.session_state.video_path)
            
            # Download button
            with open(st.session_state.video_path, 'rb') as video_file:
                st.download_button(
                    label="📥 Download Video",
                    data=video_file.read(),
                    file_name=f"studio_video_{int(os.path.getmtime(__file__))}.mp4",
                    mime="video/mp4"
                )
        else:
            st.error("Video file not found. Please try generating again.")


if __name__ == "__main__":
    main()
