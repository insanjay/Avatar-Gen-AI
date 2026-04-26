import streamlit as st
from pipeline_adapter import run_pipeline

st.set_page_config(layout="centered")

st.title("🎬 AI Video Generator")

# Avatar (required)
avatar = st.file_uploader("Upload Avatar Image (Required)", type=["jpg", "png", "jpeg"])

# Inputs
text_input = st.text_area("Text (optional)")
pdf_file = st.file_uploader("PDF (optional)", type=["pdf"])
audio_file = st.file_uploader("Audio (optional)", type=["mp3", "wav"])

has_input = bool(text_input.strip()) or pdf_file or audio_file
can_send = avatar and has_input

# State
if "running" not in st.session_state:
    st.session_state.running = False

if "video_path" not in st.session_state:
    st.session_state.video_path = None

# Button
if st.button("Generate Video", disabled=not can_send) and not st.session_state.running:

    st.session_state.running = True

    avatar_bytes = avatar.read()
    pdf_bytes = pdf_file.read() if pdf_file else None
    audio_bytes = audio_file.read() if audio_file else None

    try:
        with st.spinner("Generating video..."):
            video_path = run_pipeline(
                text=text_input,
                pdf_bytes=pdf_bytes,
                audio_bytes=audio_bytes,
                image_bytes=avatar_bytes
            )

        st.session_state.video_path = video_path
        st.success("Video Generated")

    except Exception as e:
        st.error(str(e))

    finally:
        st.session_state.running = False

# Display video
if st.session_state.video_path:
    st.video(st.session_state.video_path)