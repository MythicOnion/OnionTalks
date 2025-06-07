import streamlit as st
import io
import numpy as np
import whisper
import torch
import tempfile
import os
import collections

# Initialize PyTorch's backend safely to avoid potential issues with CUDA or CPU tensor operations
try:
    if torch.cuda.is_available():
        _ = torch.tensor([1.0]).cuda()
    _ = torch.tensor([1.0]).cpu()
except Exception as e:
    print(f"Warning: PyTorch dummy initialization failed: {e}")
    pass

# --- Configuration ---
CHUNK_LENGTH_SECONDS = 1
MIC_RECORDER_DEFAULT_SAMPLE_RATE = 44100

@st.cache_resource
def load_whisper_model(model_size):
    """
    Load the Whisper model for speech-to-text transcription.

    This function loads the specified Whisper model onto the available device (GPU if available, otherwise CPU).

    Parameters:
    - model_size (str): The size of the Whisper model to load. Options include "medium", "base", and "large-v2".

    Returns:
    - model: The loaded Whisper model.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model(model_size, device=device)
    return model

def main():
    """
    Main function to run the Streamlit app for speech-to-text transcription using Whisper.

    This function sets up the Streamlit interface, handles user inputs, and manages the transcription process.
    """
    # Set page configuration
    st.set_page_config(
        page_title="OnionTalks",
        page_icon="🧅",
    )

    st.title("🧅 OnionTalks")
    st.markdown("Speech-To-Text using Whisper")
    st.info("Click 'Start Recording' to begin recording. Make sure your recording is at least 5 seconds long!", icon="ℹ️")

    # Sidebar for settings
    st.sidebar.title("⚙️ Settings")
    WHISPER_MODEL_SIZE = st.sidebar.selectbox("Which Whisper-model would you like to use?", ("medium", "base", "large-v2"))
    debug_mode = st.sidebar.checkbox("Debug-mode")

    # Initialize session state variables for transcript, audio data, and transcription status
    if "transcript" not in st.session_state:
        st.session_state.transcript = ""
    if "audio_data" not in st.session_state:
        st.session_state.audio_data = None
    if "transcribed" not in st.session_state:
        st.session_state.transcribed = False

    # Load the Whisper model
    model = load_whisper_model(WHISPER_MODEL_SIZE)

    st.write("---")
    st.subheader("🎤 Microphone Input")

    # Audio input from the microphone
    audio_recording = st.audio_input("Record your audio by pressing the 🎙️ icon.", help = "When you're done, press the circular stop-button that has taken its place.")

    st.markdown("---")

    st.subheader("✍️ Transcript")

    # Initialize the transcript display area
    if "transcript_display_area" not in st.session_state:
        st.session_state.transcript_display_area = st.empty()

    # Debug log display area
    debug_log_display_area = None
    if debug_mode:
        if "debug_log_placeholder" not in st.session_state:
            st.session_state.debug_log_placeholder = st.sidebar.empty()
        debug_log_display_area = st.session_state.debug_log_placeholder.container()
        debug_log_display_area.markdown("--- Debug Log ---")
    elif "debug_log_placeholder" in st.session_state:
        st.session_state.debug_log_placeholder.empty()
        del st.session_state.debug_log_placeholder

    # Process and transcribe the audio if it hasn't been transcribed yet
    if audio_recording and not st.session_state.transcribed:
        audio_data = audio_recording.read()
        st.session_state.audio_data = audio_data

        if audio_data:
            st.session_state.transcribed = True
            process_and_transcribe_buffer(model, audio_data, debug_mode, debug_log_display_area)

    # Display download buttons for audio and transcript if they exist
    if st.session_state.audio_data:
        download_mp3 = st.sidebar.download_button(
            label="🎙️ Download audio-recording",
            data=st.session_state.audio_data,
            file_name="Recording.mp3",
            mime="audio/mpeg",
            icon=":material/download:",
            type="primary"
        )

    if st.session_state.transcribed:
        download_txt = st.sidebar.download_button(
            label="📜 Download transcript as .txt-file",
            data=st.session_state.transcript,
            file_name="transcript.txt",
            icon=":material/download:",
            type="primary",
            mime="text/plain"
        )

    # Reset button to clear transcript and audio data
    if st.sidebar.button("✍️ Repeat transcription"):
        st.session_state.transcript = ""
        st.session_state.audio_data = None
        st.session_state.transcribed = False
        st.session_state.transcript_display_area.empty()
        st.rerun()

    # Display the transcript
    st.session_state.transcript_display_area.markdown(
        st.session_state.transcript if st.session_state.transcript else "*No transcription yet.*"
    )

def process_and_transcribe_buffer(model, audio_data, debug_mode, debug_log_container=None):
    """
    Process and transcribe the provided audio data using the Whisper model.

    This function takes audio data, saves it to a temporary file, and uses the Whisper model
    to transcribe the audio into text. It handles the transcription process and logs debug
    information if debug mode is enabled.

    Parameters:
    - model: The loaded Whisper model used for transcribing audio to text.
    - audio_data (bytes): The binary audio data to be transcribed.
    - debug_mode (bool): Flag indicating whether debug logging is enabled.
    - debug_log_container (streamlit.container): Optional container for displaying debug logs.

    Returns:
    - None: The function updates the session state with the transcript directly.
    """
    st.session_state.transcript = ""
    st.session_state.transcript_display_area = st.empty()

    def d_write(message):
        """
        Helper function to write debug messages to the debug log container if debug mode is enabled.

        Parameters:
        - message (str): The debug message to be written.
        """
        if debug_mode and debug_log_container:
            try:
                debug_log_container.write(message)
            except Exception as e:
                print(f"Debug write error: {e}")

    with st.spinner("Transcribing...", show_time=True):
        d_write("--- Entering process_and_transcribe_buffer ---")

        temp_audio_file_path = None
        try:
            # Write audio data to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(audio_data)
                temp_audio_file_path = temp_audio_file.name
            d_write(f"Temporary audio file: {temp_audio_file_path}")

            # Transcribe the audio file using the Whisper model
            transcribed_text = model.transcribe(temp_audio_file_path)["text"]
            d_write(f"Whisper transcribed: '{transcribed_text}'")

            if transcribed_text and transcribed_text.strip():
                st.session_state.transcript = transcribed_text.strip()
                d_write(f"Session transcript updated: '{st.session_state.transcript}'")
            else:
                d_write("Transcription resulted in empty text.")

        except Exception as e:
            st.error(f"Transcription error: {e}")
            d_write(f"ERROR during transcription: {e}")
        finally:
            # Clean up: Remove the temporary audio file
            if temp_audio_file_path and os.path.exists(temp_audio_file_path):
                try:
                    os.remove(temp_audio_file_path)
                    d_write(f"Temporary file deleted: {temp_audio_file_path}")
                except Exception as e_del:
                    d_write(f"Error deleting temp file: {e_del}")
        d_write("--- Exiting process_and_transcribe_buffer ---")

if __name__ == "__main__":
    main()
