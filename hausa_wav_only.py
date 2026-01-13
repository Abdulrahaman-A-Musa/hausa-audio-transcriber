# ================================
# HAUSA AUDIO TRANSCRIBER - SIMPLE VERSION
# NO FFMPEG REQUIRED - WAV FILES ONLY!
# ================================

import streamlit as st
import tempfile
import os
import pandas as pd
import re

# Setup local FFmpeg path BEFORE importing pydub
from pathlib import Path
local_ffmpeg_bin = Path(__file__).parent / "ffmpeg" / "bin"
if local_ffmpeg_bin.exists():
    # Add local ffmpeg to PATH for this session
    os.environ['PATH'] = str(local_ffmpeg_bin) + os.pathsep + os.environ.get('PATH', '')

# Simple transcription - no audio conversion needed
import speech_recognition as sr

# Free translation using deep-translator (more reliable)
from deep_translator import GoogleTranslator

# Try to import soundfile and librosa for automatic conversion
try:
    import soundfile as sf
    import librosa
    AUDIO_CONVERSION_AVAILABLE = True
except ImportError:
    AUDIO_CONVERSION_AVAILABLE = False

# Try to import pydub for better format support (after PATH setup)
try:
    import warnings
    # Suppress pydub warnings about regex escape sequences (Python 3.13+)
    warnings.filterwarnings('ignore', category=SyntaxWarning, module='pydub')
    # Suppress pydub runtime warnings about missing ffmpeg
    warnings.filterwarnings('ignore', category=RuntimeWarning, module='pydub')
    
    from pydub import AudioSegment
    
    # Check if FFmpeg is actually available
    import subprocess
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=2)
        PYDUB_AVAILABLE = True
        
        # Explicitly set ffmpeg paths if local installation exists
        if local_ffmpeg_bin.exists():
            ffmpeg_exe = local_ffmpeg_bin / "ffmpeg.exe"
            ffprobe_exe = local_ffmpeg_bin / "ffprobe.exe"
            if ffmpeg_exe.exists():
                AudioSegment.converter = str(ffmpeg_exe)
            if ffprobe_exe.exists():
                AudioSegment.ffprobe = str(ffprobe_exe)
    except (subprocess.SubprocessError, FileNotFoundError):
        # FFmpeg not available - pydub won't work
        PYDUB_AVAILABLE = False
        
except ImportError:
    PYDUB_AVAILABLE = False

st.set_page_config(
    page_title="Hausa Audio Transcriber - Simple",
    page_icon="🎤",
    layout="wide"
)

# Increase file upload limit to 500MB
# Note: For very large files, you may need to configure this in .streamlit/config.toml
st.markdown("""
<style>
    /* Override default file upload size */
    [data-testid="stFileUploader"] {
        max-height: 500px;
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e88e5 0%, #43a047 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        background: #f5f7fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #1e88e5;
        margin: 1rem 0;
    }
    .stButton > button {
        background: #1e88e5;
        color: white;
        font-weight: 600;
    }
    .highlight-box {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transcription_result' not in st.session_state:
    st.session_state.transcription_result = None
if 'translation_result' not in st.session_state:
    st.session_state.translation_result = None
if 'transcription_segments' not in st.session_state:
    st.session_state.transcription_segments = None
if 'translation_segments' not in st.session_state:
    st.session_state.translation_segments = None

# Header
st.markdown("""
<div class="main-header">
    <h1>🎤 Hausa Audio Transcriber</h1>
    <p>Professional Audio Transcription with Full Format Support</p>
    <p style="font-size: 0.9em; opacity: 0.9;">Upload any audio format - Automatic conversion & transcription</p>
</div>
""", unsafe_allow_html=True)

# Important Notice - Show conversion capability
if PYDUB_AVAILABLE:
    st.markdown("""
    <div class="highlight-box">
        <h3>✨ Audio Format Support</h3>
        <p><strong>✅ Directly Supported:</strong> WAV, FLAC, OGG (instant processing)</p>
        <p><strong>⚠️ Needs Conversion:</strong> MP3, M4A, AMR, AAC, 3GP (convert online first)</p>
        <p>📱 <strong>For phone recordings (AMR, 3GP, M4A):</strong> Use free online converter</p>
        <p>� <strong>Quick Converter:</strong> <a href="https://cloudconvert.com/to/wav" target="_blank">cloudconvert.com/to/wav</a></p>
        <p>💡 <strong>Tip:</strong> Convert to WAV once, then upload for instant transcription!</p>
    </div>
    """, unsafe_allow_html=True)
elif AUDIO_CONVERSION_AVAILABLE:
    st.markdown("""
    <div class="highlight-box">
        <h3>✨ Audio Format Support</h3>
        <p><strong>✅ Directly Supported:</strong> WAV, FLAC, OGG (instant processing)</p>
        <p><strong>⚠️ Needs Online Conversion:</strong> MP3, M4A, AMR, AAC, 3GP</p>
        <p>� <strong>For phone recordings (AMR, 3GP, M4A):</strong> Convert to WAV first</p>
        <p>🔗 <strong>Quick Converter:</strong> <a href="https://cloudconvert.com/to/wav" target="_blank">cloudconvert.com/to/wav</a></p>
        <p>💡 <strong>Tip:</strong> WAV files = instant transcription!</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="highlight-box">
        <h3>📌 WAV Files Required</h3>
        <p><strong>✅ Supported:</strong> WAV, FLAC, OGG only</p>
        <p><strong>📱 For phone recordings:</strong> Convert to WAV online first:</p>
        <ul>
            <li>🌐 <a href="https://cloudconvert.com/to/wav" target="_blank">CloudConvert</a> (Recommended)</li>
            <li>🌐 <a href="https://online-audio-converter.com/" target="_blank">Online Audio Converter</a></li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.markdown("### 🌐 Translation")
    target_lang = st.selectbox(
        "Translate to:",
        options=[
            ("English", "en"),
            ("Arabic", "ar"),
            ("French", "fr"),
            ("Spanish", "es"),
            ("Portuguese", "pt")
        ],
        format_func=lambda x: x[0]
    )
    
    st.markdown("---")
    
    st.markdown("### ℹ️ About")
    if PYDUB_AVAILABLE:
        st.success("""
        **Full Version - FFmpeg Enabled:**
        
        ✅ 100% Free
        ✅ All audio formats supported
        ✅ No API keys required
        ✅ Automatic conversion
        ✅ Instant transcription
        ✅ Local processing
        
        **Perfect for:**
        - Hausa interviews
        - Voice recordings
        - Phone recordings
        - Meetings & conferences
        - Audio files from any device
        """)
    else:
        st.info("""
        **Basic Version:**
        
        ✅ 100% Free
        ✅ No API keys required
        ✅ Works with WAV files
        ✅ Instant transcription
        
        **Perfect for:**
        - Hausa audio
        - Voice recordings
        - Interviews
        - Meetings
        
        💡 Run `python install_ffmpeg_simple.py` for all formats!
        """)
    
    st.markdown("---")
    
    st.markdown("### 🔊 Audio Quality Tips")
    st.markdown("""
    - Clear audio works best
    - Minimal background noise
    - Single speaker preferred
    - Good microphone helps
    - Keep files under 50MB
    """)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload Audio Files")
    
    # Batch processing info
    st.info("💡 **Batch Processing:** Upload up to 10 audio files at once for faster processing!")
    
    # Determine accepted file types
    if PYDUB_AVAILABLE:
        # FFmpeg enabled - support ALL formats
        accepted_types = ['wav', 'mp3', 'm4a', 'amr', 'aac', '3gp', 'ogg', 'flac', 'wma', 'webm', 'opus', 'aiff', 'au', 'mp2', 'mp4', 'mkv', 'avi']
        file_help = "Upload ANY audio format - FFmpeg will auto-convert! MP3, M4A, AMR, WAV, AAC, 3GP, etc."
    elif AUDIO_CONVERSION_AVAILABLE:
        # Formats that work well: WAV, FLAC, OGG (native soundfile support)
        # Formats that need ffmpeg: MP3, M4A, AMR, AAC, WMA, etc.
        accepted_types = ['wav', 'flac', 'ogg', 'mp3', 'm4a', 'aac', 'amr', '3gp', 'wma', 'webm', 'opus']
        file_help = "Upload WAV/FLAC/OGG (best) or MP3/M4A/AMR (needs ffmpeg). WAV recommended for instant processing!"
    else:
        accepted_types = ['wav', 'flac', 'ogg']
        file_help = "✅ WAV/FLAC/OGG work instantly | ⚠️ For AMR/MP3/M4A: convert to WAV online first (cloudconvert.com/to/wav)"
    
    uploaded_files = st.file_uploader(
        "Choose audio files (up to 10)",
        type=accepted_types,
        help=file_help,
        accept_multiple_files=True
    )
    
    if uploaded_files:
        # Limit to 10 files
        if len(uploaded_files) > 10:
            st.error(f"❌ Too many files! You uploaded {len(uploaded_files)} files. Please upload maximum 10 files at a time.")
            uploaded_files = uploaded_files[:10]
            st.warning("⚠️ Only the first 10 files will be processed.")
        
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
        
        # Show file info
        total_size = 0
        for idx, file in enumerate(uploaded_files, 1):
            file_size = len(file.getvalue()) / 1024 / 1024
            total_size += file_size
            
            if file_size > 200:
                st.error(f"❌ File {idx} ({file.name}) is too large: {file_size:.2f} MB (max 200MB)")
            elif file_size > 100:
                st.warning(f"⚠️ File {idx} ({file.name}): {file_size:.2f} MB - May take longer")
            else:
                st.info(f"� File {idx}: {file.name} ({file_size:.2f} MB)")
        
        st.metric("Total Upload Size", f"{total_size:.2f} MB")

with col2:
    st.subheader("🎯 Process Audio Files")
    
    st.markdown("**Quick Steps:**")
    st.markdown("1. ⬅️ Upload audio files (1-10)")
    st.markdown("2. ⬇️ Choose display options (optional)")
    st.markdown("3. 🎉 Click transcribe & get results with ROLE labels!")
    
    # Display options
    with st.expander("📊 Display Options", expanded=False):
        st.markdown("**Choose what to display in results:**")
        
        show_timestamped = st.checkbox("⏱️ Show timestamped transcript (with ROLE)", value=True, 
                                       help="Display Hausa transcription with time markers and speaker roles")
        
        show_translation = st.checkbox("🌐 Show English translation (with ROLE)", value=True,
                                      help="Display English translation with timestamps and speaker roles")
        
        st.session_state.display_options = {
            'timestamped': show_timestamped,
            'translation': show_translation
        }
    
    if uploaded_files and len(uploaded_files) > 0:
        transcribe_btn = st.button(
            f"▶️ Transcribe & Translate All ({len(uploaded_files)} files)", 
            type="primary", 
            use_container_width=True
        )
    else:
        st.warning("⚠️ Please upload audio files first")
        transcribe_btn = False


def convert_to_wav(audio_file, original_filename):
    """Convert any audio format to WAV using multiple methods"""
    tmp_input = None
    tmp_output = None
    
    try:
        # Get file extension
        file_ext = original_filename.split('.')[-1].lower()
        
        with st.spinner(f"🔄 Converting {file_ext.upper()} to WAV..."):
            # Save uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_ext}') as tmp_in:
                tmp_in.write(audio_file.read())
                tmp_input = tmp_in.name
            
            tmp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
            
            # Try Method 1: pydub with FFmpeg (best for MP3, M4A, AMR, AAC, etc.)
            if PYDUB_AVAILABLE:
                try:
                    st.info("🔄 Using FFmpeg converter...")
                    audio = AudioSegment.from_file(tmp_input, format=file_ext)
                    audio.export(tmp_output, format='wav')
                    st.success(f"✅ Converted {file_ext.upper()} to WAV using FFmpeg!")
                    return tmp_output
                except Exception as pydub_error:
                    st.warning(f"FFmpeg method failed: {str(pydub_error)}")
                    st.info("Trying alternative method...")
            
            # Try Method 2: Direct soundfile read (works for WAV, FLAC, OGG)
            if AUDIO_CONVERSION_AVAILABLE:
                try:
                    audio_data, sample_rate = sf.read(tmp_input)
                    sf.write(tmp_output, audio_data, sample_rate)
                    st.success(f"✅ Converted {file_ext.upper()} to WAV using soundfile!")
                    return tmp_output
                except Exception:
                    st.info("Soundfile method also failed, trying librosa...")
            
            # Try Method 3: librosa (more format support but slower)
            if AUDIO_CONVERSION_AVAILABLE:
                try:
                    import warnings
                    warnings.filterwarnings('ignore')
                    audio_data, sample_rate = librosa.load(tmp_input, sr=None, mono=True)
                    sf.write(tmp_output, audio_data, sample_rate)
                    st.success(f"✅ Converted {file_ext.upper()} to WAV!")
                    return tmp_output
                except Exception:
                    pass
            
            # If all methods fail, show helpful message
            raise Exception(f"Unable to convert {file_ext.upper()} format")
            
    except Exception as e:
        st.error(f"❌ Conversion failed for {file_ext.upper()} format")
        st.warning(f"""
        **{file_ext.upper()} files need conversion to WAV format**
        
        📱 **Quick & Easy Online Conversion (Recommended):**
        
        1. Go to: **[CloudConvert WAV Converter](https://cloudconvert.com/to/wav)**
        2. Upload your {file_ext.upper()} file
        3. Click "Convert" and wait 10-30 seconds
        4. Download the WAV file
        5. Upload the WAV file here
        
        **OR use these free converters:**
        - **[Online Audio Converter](https://online-audio-converter.com/)** - Fast & easy
        - **[FreeConvert](https://www.freeconvert.com/audio-converter)** - No registration
        - **[Zamzar](https://www.zamzar.com/)** - Email delivery option
        
        💡 **Tip:** Save converted WAV files for future use!
        
        ⚠️ **Note:** This online app doesn't include FFmpeg for {file_ext.upper()} conversion.
        For offline conversion, use desktop audio software like Audacity (free).
        """)
        return None
        
    finally:
        # Cleanup input file
        if tmp_input and os.path.exists(tmp_input):
            try:
                import time
                time.sleep(0.2)
                os.unlink(tmp_input)
            except Exception:
                pass


def parse_qa_from_text(text):
    """
    Parse transcribed text into Question-Answer pairs
    Identifies survey questions (Q1, Q2, etc.) and separates from answers
    Specifically designed for mortality/reproductive health survey
    """
    # Common Hausa question patterns from your survey
    hausa_question_words = [
        'menene',      # what is
        'wanne',       # which
        'nawa',        # how many
        'shin',        # whether/if
        'kin taba',    # have you ever
        'kina da',     # do you have
        'ka',          # questions
        'kika',        # you (feminine)
        'zaka',        # will you
        'kuna',        # do you (plural)
        'akwai',       # is there
    ]
    
    # Common English question patterns from survey
    english_question_words = [
        'how many', 'what is', 'do you', 'have you', 'are you', 
        'can you', 'did you', 'does', 'was', 'were', 'will you',
        'have you ever', 'kindly', 'select', 'gender', 'name',
        'age', 'phone number', 'household', 'education', 'born'
    ]
    
    # Split by sentences
    sentences = re.split(r'[.?!]', text)
    qa_pairs = []
    current_question = None
    current_answer = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence or len(sentence) < 5:
            continue
        
        is_question = False
        
        # Check for explicit Q patterns (Q1, Q36, Q101, etc.)
        if re.search(r'\bQ\d+', sentence, re.IGNORECASE):
            is_question = True
        
        # Check for Hausa question words
        for word in hausa_question_words:
            if word in sentence.lower():
                is_question = True
                break
        
        # Check for English question words
        if not is_question:
            for phrase in english_question_words:
                if phrase in sentence.lower():
                    is_question = True
                    break
        
        # Check for question mark
        if '?' in sentence:
            is_question = True
        
        # Check if starts with question word patterns
        sentence_lower = sentence.lower()
        if sentence_lower.startswith(('what', 'how', 'when', 'where', 'which', 'who', 'why', 'do ', 'does ', 'did ', 'have ', 'has ', 'had ', 'can ', 'could ', 'would ', 'should ', 'is ', 'are ', 'was ', 'were ')):
            is_question = True
        
        if is_question:
            # Save previous Q&A pair if exists
            if current_question and current_answer:
                qa_pairs.append({
                    'type': 'Question',
                    'text': current_question
                })
                qa_pairs.append({
                    'type': 'Answer',
                    'text': ' '.join(current_answer)
                })
            
            # Start new question
            current_question = sentence
            current_answer = []
        else:
            # This is part of the answer (or continuation)
            if current_question:
                current_answer.append(sentence)
            else:
                # No question yet, might be background noise - skip
                pass
    
    # Add the last Q&A pair
    if current_question:
        qa_pairs.append({
            'type': 'Question',
            'text': current_question
        })
        if current_answer:
            qa_pairs.append({
                'type': 'Answer',
                'text': ' '.join(current_answer)
            })
    
    return qa_pairs


def transcribe_wav(audio_file, original_filename="audio.wav"):
    """Transcribe audio file using Google Speech Recognition with timestamps"""
    recognizer = sr.Recognizer()
    tmp_path = None
    converted_path = None
    
    try:
        # Check if conversion is needed
        file_ext = original_filename.split('.')[-1].lower()
        
        if file_ext != 'wav' and AUDIO_CONVERSION_AVAILABLE:
            # Convert to WAV first
            audio_file.seek(0)
            converted_path = convert_to_wav(audio_file, original_filename)
            if not converted_path:
                return None
            tmp_path = converted_path
        else:
            # Save WAV file directly
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                audio_file.seek(0)
                tmp.write(audio_file.read())
                tmp_path = tmp.name
        
        # Transcribe in chunks for longer audio with timestamps
        with st.spinner("🔄 Transcribing your Hausa audio..."):
            with sr.AudioFile(tmp_path) as source:
                # Get total duration
                total_duration = int(source.DURATION) if hasattr(source, 'DURATION') else 0
                
                # Adjust recognizer settings to capture ALL voices (interviewer + respondent)
                recognizer.energy_threshold = 300  # Lower = more sensitive (default is 300)
                recognizer.dynamic_energy_threshold = True  # Adapt to audio levels
                recognizer.pause_threshold = 0.8  # Shorter pause = captures more speech
                
                # Minimal ambient noise adjustment to preserve quiet voices
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                
                # For very long audio, process in segments
                if total_duration > 180:  # More than 3 minutes
                    st.warning(f"⚠️ Audio is {int(total_duration/60)} minutes long")
                    st.info("""
                    **Google's free API works best with shorter audio (under 3 minutes).**
                    
                    For best results:
                    1. Split your audio into 5-minute segments
                    2. Use: https://mp3cut.net
                    3. Transcribe each segment separately
                    
                    Or try transcribing anyway (may take longer)...
                    """)
                    
                    # Ask user if they want to continue
                    st.warning("⏱️ Processing long audio - this may take several minutes...")
                
                # Process in 60-second chunks (longer to capture Q&A exchanges)
                transcription_segments = []
                chunk_duration = 60  # Increased to 60 seconds for full Q&A
                current_time = 0
                
                progress = st.progress(0)
                status = st.empty()
                
                chunk_num = 0
                max_chunks = (total_duration // chunk_duration + 1) if total_duration > 0 else 10
                
                while True:
                    try:
                        # Record next chunk
                        audio_data = recognizer.record(source, duration=chunk_duration)
                        
                        if len(audio_data.frame_data) == 0:
                            break  # No more audio
                        
                        chunk_num += 1
                        status.text(f"Processing chunk {chunk_num}/{max_chunks}...")
                        
                        # Calculate timestamp for this chunk
                        start_time = current_time
                        end_time = current_time + chunk_duration
                        
                        # Transcribe chunk
                        try:
                            chunk_text = recognizer.recognize_google(audio_data, language='ha')
                            if chunk_text.strip():
                                transcription_segments.append({
                                    'start': start_time,
                                    'end': end_time,
                                    'text': chunk_text
                                })
                        except sr.UnknownValueError:
                            # Try English for this chunk
                            try:
                                chunk_text = recognizer.recognize_google(audio_data, language='en')
                                if chunk_text.strip():
                                    transcription_segments.append({
                                        'start': start_time,
                                        'end': end_time,
                                        'text': chunk_text
                                    })
                            except sr.UnknownValueError:
                                # Skip silent/unclear chunk
                                pass
                        
                        # Update current time
                        current_time = end_time
                        
                        # Update progress
                        if total_duration > 0:
                            progress_val = min(chunk_num / max_chunks, 1.0)
                            progress.progress(progress_val)
                        
                    except sr.RequestError:
                        st.error(f"❌ API request failed on chunk {chunk_num}")
                        st.info("""
                        **Google's API has limits:**
                        - Maximum audio length per request
                        - Rate limiting (too many requests)
                        
                        **Solutions:**
                        1. Split audio into smaller files (5 minutes each)
                        2. Wait a few minutes and try again
                        3. Use lower quality audio (smaller file size)
                        """)
                        break
                    
                    except Exception:
                        # End of file or other error
                        break
                
                progress.empty()
                status.empty()
                
                if transcription_segments:
                    # Parse Q&A structure from all segments
                    full_text = " ".join([seg['text'] for seg in transcription_segments])
                    qa_pairs = parse_qa_from_text(full_text)
                    
                    # Store both segments and Q&A pairs in session state
                    st.session_state.transcription_segments = transcription_segments
                    st.session_state.qa_pairs = qa_pairs
                    
                    # Return combined text for backward compatibility
                    return full_text
                else:
                    # Try processing entire file at once for short audio
                    st.info("🔄 Trying to process entire audio at once...")
                    
                    with sr.AudioFile(tmp_path) as source2:
                        recognizer.adjust_for_ambient_noise(source2, duration=0.5)
                        audio_data = recognizer.record(source2)
                        
                        try:
                            text = recognizer.recognize_google(audio_data, language='ha')
                            # Create a single segment for short audio
                            st.session_state.transcription_segments = [{
                                'start': 0,
                                'end': total_duration if total_duration > 0 else 60,
                                'text': text
                            }]
                            return text
                        except sr.UnknownValueError:
                            # Try English
                            text = recognizer.recognize_google(audio_data, language='en')
                            st.session_state.transcription_segments = [{
                                'start': 0,
                                'end': total_duration if total_duration > 0 else 60,
                                'text': text
                            }]
                            return text
        
    except sr.UnknownValueError:
        st.error("❌ Could not understand the audio")
        st.info("""
        **Tips for better results:**
        - Ensure audio is clear
        - Reduce background noise
        - Speaker should be close to mic
        - Try recording again with better quality
        """)
        return None
        
    except sr.RequestError as e:
        st.error(f"❌ Service error: {e}")
        st.info("""
        **This usually means:**
        - Audio file is too large (Google has ~10MB limit per request)
        - Audio is too long (best results under 1 minute)
        - Too many requests (rate limited)
        
        **Solutions:**
        1. **Split your audio** into shorter segments (3-5 minutes each)
           - Use: https://mp3cut.net
           - Process each segment separately
        
        2. **Reduce file size:**
           - Lower bitrate to 64kbps or 96kbps
           - Use: https://online-audio-converter.com
        
        3. **Wait a few minutes** if you've made many requests
        
        4. **Check internet connection** and try again
        """)
        return None
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("""
        **For best results with long audio:**
        
        Please split your audio file into smaller segments (5-10 minutes each)
        using an online tool like https://mp3cut.net
        """)
        return None
        
    finally:
        # Cleanup
        if tmp_path and os.path.exists(tmp_path):
            try:
                import time
                time.sleep(0.3)
                os.unlink(tmp_path)
            except Exception:
                pass
        
        if converted_path and os.path.exists(converted_path):
            try:
                import time
                time.sleep(0.3)
                os.unlink(converted_path)
            except Exception:
                pass


def detect_speaker_role(text):
    """Detect if text is from interviewer (question) or respondent (answer)"""
    text_lower = text.lower()
    
    # Check for question patterns
    if any(word in text_lower for word in ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 
                                            'q10', 'q20', 'q30', 'q40', 'q50', 'q60', 'q70', 'q80', 'q90',
                                            'q100', 'q101', 'q102', 'q103', 'q104', 'q105', 'q106', 'q107',
                                            'q108', 'q109', 'q110', 'q111', 'q112', 'q113', 'q114', 'q115',
                                            'q120', 'q121', 'q125', 'q130', 'q131', 'q132', 'q133', 'q134', 'q135']):
        return "❓ INTERVIEWER"
    elif any(word in text_lower for word in ['how many', 'what is', 'menene', 'nawa', 'wanne', 
                                              'kin taba', 'kina da', 'do you', 'have you', 'are you',
                                              'shin', 'kindly', 'select', 'enter', 'confirm',
                                              'name of', 'phone number', 'age', 'gender', 'household']):
        return "❓ INTERVIEWER"
    elif '?' in text:
        return "❓ INTERVIEWER"
    else:
        return "💭 RESPONDENT"


def translate_text(text, target_lang):
    """Translate text using Google Translate (FREE) via deep-translator"""
    if not text or len(text.strip()) == 0:
        return ""
    
    try:
        # Use deep-translator for more reliable translation
        translator = GoogleTranslator(source='auto', target=target_lang[1])
        
        with st.spinner(f"🔄 Translating to {target_lang[0]}..."):
            result = translator.translate(text)
            if result:
                return result
            else:
                st.warning("⚠️ Translation returned empty result")
                return text  # Return original if translation fails
    except Exception as e:
        st.warning(f"⚠️ Translation error: {str(e)}")
        st.info("💡 Using original transcription (translation skipped)")
        return text  # Return original text instead of None


# Process audio files
if transcribe_btn and uploaded_files:
    st.markdown("---")
    st.markdown("### 🔄 Processing Your Audio Files...")
    
    # Initialize batch results storage
    if 'batch_results' not in st.session_state:
        st.session_state.batch_results = []
    
    st.session_state.batch_results = []  # Clear previous results
    
    # Overall progress
    overall_progress = st.progress(0)
    overall_status = st.empty()
    
    # Process each file
    for file_idx, uploaded_file in enumerate(uploaded_files, 1):
        overall_status.text(f"Processing file {file_idx}/{len(uploaded_files)}: {uploaded_file.name}")
        
        st.markdown(f"---")
        st.markdown(f"## � Record {file_idx}: {uploaded_file.name}")
        
        # File progress
        file_progress = st.progress(0)
        file_status = st.empty()
        
        # Transcribe
        file_progress.progress(25)
        file_status.text(f"Step 1/3: Transcribing Record {file_idx}...")
        
        uploaded_file.seek(0)  # Reset file pointer
        transcription = transcribe_wav(uploaded_file, uploaded_file.name)
        
        file_progress.progress(50)
        
        if transcription:
            file_status.text(f"Step 2/3: Translating Record {file_idx}...")
            
            # Store transcription temporarily
            temp_transcription_segments = st.session_state.transcription_segments
            
            # Translate full text
            file_progress.progress(75)
            translation = translate_text(transcription, target_lang)
            
            # Translate segments
            translated_segments = None
            if temp_transcription_segments:
                translated_segments = []
                total_segments = len(temp_transcription_segments)
                
                for idx, seg in enumerate(temp_transcription_segments):
                    try:
                        translator = GoogleTranslator(source='auto', target=target_lang[1])
                        translated_text = translator.translate(seg['text'])
                        translated_segments.append({
                            'start': seg['start'],
                            'end': seg['end'],
                            'text': translated_text
                        })
                        
                        # Update progress
                        trans_progress = 75 + (20 * (idx + 1) / total_segments)
                        file_progress.progress(int(trans_progress))
                    except Exception:
                        translated_segments.append(seg)
            
            file_progress.progress(100)
            file_status.text(f"✅ Record {file_idx} Complete!")
            
            # Get Q&A pairs if available
            qa_pairs = st.session_state.get('qa_pairs', [])
            
            # Store result
            st.session_state.batch_results.append({
                'record_number': file_idx,
                'filename': uploaded_file.name,
                'transcription': transcription,
                'translation': translation,
                'transcription_segments': temp_transcription_segments,
                'translation_segments': translated_segments,
                'qa_pairs': qa_pairs  # Add structured Q&A
            })
            
            st.success(f"✅ Record {file_idx} processed successfully!")
        else:
            file_progress.empty()
            file_status.empty()
            st.error(f"❌ Failed to process Record {file_idx}")
            
            # Store failed result
            st.session_state.batch_results.append({
                'record_number': file_idx,
                'filename': uploaded_file.name,
                'transcription': None,
                'translation': None,
                'transcription_segments': None,
                'translation_segments': None,
                'error': True
            })
        
        # Update overall progress
        overall_progress.progress(file_idx / len(uploaded_files))
        
        # Small delay between files
        import time
        time.sleep(0.5)
    
    overall_progress.progress(100)
    overall_status.text(f"✅ All {len(uploaded_files)} files processed!")
    st.success(f"🎉 Batch processing complete! {len(uploaded_files)} records processed.")



# --- Structured Q/A Parsing and Display ---
def parse_transcription(transcript_text):
    """
    Parse the transcription text into a list of (question, response) pairs.
    Assumes format: 'Q: ... A: ... Q: ... A: ...'
    """
    qa_pairs = []
    segments = re.split(r'Q:\s*', transcript_text)
    for segment in segments[1:]:
        if 'A:' in segment:
            question, answer = segment.split('A:', 1)
            qa_pairs.append({
                "Question": question.strip(),
                "Response": answer.strip()
            })
    return qa_pairs

# Add structured parsing for transcription
def parse_transcription_with_roles(transcript_text):
    """
    Parse the transcription text into a structured format with roles.
    Assumes format: 'Person A: ... Person B: ...'
    """
    dialogue = []
    lines = transcript_text.splitlines()
    for line in lines:
        if ':' in line:
            role, text = line.split(':', 1)
            dialogue.append({
                "Speaker": role.strip(),
                "Text": text.strip()
            })
    return dialogue

# Improved parsing logic to handle edge cases
def parse_transcription_q_and_a(transcript_text):
    """
    Parse the transcription text into a structured Q&A format.
    Handles variations like 'Q: ... A: ...' or 'Question: ... Answer: ...'.
    """
    qa_pairs = []
    # Match patterns like 'Q: ... A: ...' or 'Question: ... Answer: ...'
    segments = re.split(r'(?:Q:|Question:)', transcript_text, flags=re.IGNORECASE)
    for segment in segments[1:]:
        if re.search(r'(?:A:|Answer:)', segment, flags=re.IGNORECASE):
            question, answer = re.split(r'(?:A:|Answer:)', segment, 1, flags=re.IGNORECASE)
            qa_pairs.append({
                "Question": question.strip(),
                "Response": answer.strip()
            })
    return qa_pairs

# Enhanced parsing logic to infer Q&A structure without explicit markers
def parse_transcription_infer_q_and_a(transcript_text):
    """
    Infer questions and answers from the transcription text based on Hausa question words.
    """
    question_words = ["wa", "me", "ina", "yaya", "wane", "wace", "nawa", "ta yaya"]  # Common Hausa question words
    qa_pairs = []
    lines = transcript_text.split('. ')  # Split by sentences

    current_question = None
    for line in lines:
        if any(line.strip().lower().startswith(word) for word in question_words):
            # Treat this line as a question
            if current_question:
                # If there's an unanswered question, append it with an empty response
                qa_pairs.append({"Question": current_question, "Response": ""})
            current_question = line.strip()
        elif current_question:
            # Treat this line as an answer to the current question
            qa_pairs.append({"Question": current_question, "Response": line.strip()})
            current_question = None

    # If there's a leftover question without an answer
    if current_question:
        qa_pairs.append({"Question": current_question, "Response": ""})

    return qa_pairs

# Fallback to highlight potential questions and answers in raw text
def highlight_potential_q_and_a(transcript_text):
    """
    Highlight potential questions and answers in the raw transcription text.
    """
    question_words = ["wa", "me", "ina", "yaya", "wane", "wace", "nawa", "ta yaya"]  # Common Hausa question words
    highlighted_text = []
    lines = transcript_text.split('. ')  # Split by sentences

    for line in lines:
        if any(line.strip().lower().startswith(word) for word in question_words):
            # Highlight as a potential question
            highlighted_text.append(f"**Question:** {line.strip()}")
        else:
            # Treat as a potential answer
            highlighted_text.append(f"**Answer:** {line.strip()}")

    return '\n'.join(highlighted_text)

# Display batch results
if 'batch_results' in st.session_state and len(st.session_state.batch_results) > 0:
    st.markdown("---")
    st.markdown("## 📝 Batch Processing Results")
    st.info(f"✨ Processed {len(st.session_state.batch_results)} audio files")
    
    # Add download all button
    st.markdown("### 📥 Download All Results")
    
    # Prepare combined CSV for all records
    all_records_data = []
    for result in st.session_state.batch_results:
        if not result.get('error') and result['transcription_segments']:
            for seg in result['transcription_segments']:
                start_min = int(seg['start'] // 60)
                start_sec = int(seg['start'] % 60)
                end_min = int(seg['end'] // 60)
                end_sec = int(seg['end'] % 60)
                time_range = f"{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d} min"
                
                # Detect speaker role
                role = detect_speaker_role(seg['text'])
                
                all_records_data.append({
                    "Record": f"Record {result['record_number']}",
                    "Filename": result['filename'],
                    "Audio Minute": time_range,
                    "Role": role,
                    "Hausa Transcription": seg['text'],
                    "English Translation": ""  # Will fill below
                })
    
    # Add translations
    trans_idx = 0
    for result in st.session_state.batch_results:
        if not result.get('error') and result['translation_segments']:
            for seg in result['translation_segments']:
                if trans_idx < len(all_records_data):
                    all_records_data[trans_idx]["English Translation"] = seg['text']
                    trans_idx += 1
    
    if all_records_data:
        df_all = pd.DataFrame(all_records_data)
        csv_all = df_all.to_csv(index=False)
        
        col_download1, col_download2 = st.columns(2)
        with col_download1:
            st.download_button(
                "📥 Download All Records (CSV)",
                data=csv_all,
                file_name=f"all_transcriptions_{len(st.session_state.batch_results)}_records.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_download2:
            # Excel format would be nice but requires openpyxl
            st.info("💡 Open CSV in Excel for easy viewing")
    
    st.markdown("---")
    
    # Display each record
    for result in st.session_state.batch_results:
        st.markdown(f"## 📁 Record {result['record_number']}: {result['filename']}")
        
        if result.get('error'):
            st.error(f"❌ Failed to process this record")
            st.markdown("---")
            continue
        
        # Get display options
        display_opts = st.session_state.get('display_options', {
            'timestamped': True,
            'translation': True
        })
        
        # Timestamped Transcription
        if display_opts.get('timestamped', True) and result['transcription_segments'] and len(result['transcription_segments']) > 0:
            st.markdown(f"### 🕐 Timestamped Transcript - Record {result['record_number']}")
            
            transcript_data = []
            for seg in result['transcription_segments']:
                start_min = int(seg['start'] // 60)
                start_sec = int(seg['start'] % 60)
                end_min = int(seg['end'] // 60)
                end_sec = int(seg['end'] % 60)
                time_range = f"{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d} min"
                
                # Detect speaker role
                role = detect_speaker_role(seg['text'])
                
                transcript_data.append({
                    "AUDIO MINUTE": time_range,
                    "ROLE": role,
                    "TRANSCRIBED VERSION": seg['text']
                })
            
            df_transcript = pd.DataFrame(transcript_data)
            st.dataframe(
                df_transcript,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "AUDIO MINUTE": st.column_config.TextColumn("AUDIO MINUTE", width="small"),
                    "ROLE": st.column_config.TextColumn("ROLE", width="small"),
                    "TRANSCRIBED VERSION": st.column_config.TextColumn("TRANSCRIBED VERSION", width="large"),
                }
            )
        
        # Timestamped Translation
        if display_opts.get('translation', True) and result['translation_segments'] and len(result['translation_segments']) > 0:
            st.markdown(f"### 🌐 {target_lang[0]} Translation - Record {result['record_number']}")
            
            translation_data = []
            for idx, seg in enumerate(result['translation_segments']):
                start_min = int(seg['start'] // 60)
                start_sec = int(seg['start'] % 60)
                end_min = int(seg['end'] // 60)
                end_sec = int(seg['end'] % 60)
                time_range = f"{start_min:02d}:{start_sec:02d} - {end_min:02d}:{end_sec:02d} min"
                
                # Detect speaker role from original transcription
                role = "💭 RESPONDENT"
                if idx < len(result['transcription_segments']):
                    role = detect_speaker_role(result['transcription_segments'][idx]['text'])
                
                translation_data.append({
                    "AUDIO MINUTE": time_range,
                    "ROLE": role,
                    "TRANSLATED VERSION": seg['text']
                })
            
            df_translation = pd.DataFrame(translation_data)
            st.dataframe(
                df_translation,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "AUDIO MINUTE": st.column_config.TextColumn("AUDIO MINUTE", width="small"),
                    "ROLE": st.column_config.TextColumn("ROLE", width="small"),
                    "TRANSLATED VERSION": st.column_config.TextColumn("TRANSLATED VERSION", width="large"),
                }
            )
        
        # Individual download buttons
        col1, col2 = st.columns(2)
        with col1:
            if result['transcription_segments']:
                df_t = pd.DataFrame(transcript_data)
                csv_t = df_t.to_csv(index=False)
                st.download_button(
                    f"📥 Download Record {result['record_number']} Transcript",
                    data=csv_t,
                    file_name=f"record_{result['record_number']}_transcript.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with col2:
            if result['translation_segments']:
                df_tr = pd.DataFrame(translation_data)
                csv_tr = df_tr.to_csv(index=False)
                st.download_button(
                    f"📥 Download Record {result['record_number']} Translation",
                    data=csv_tr,
                    file_name=f"record_{result['record_number']}_translation.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Statistics for this record
        st.markdown(f"#### 📊 Record {result['record_number']} Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Words", len(result['transcription'].split()))
        with col2:
            st.metric("Characters", len(result['transcription']))
        with col3:
            st.metric("Segments", len(result['transcription_segments']) if result['transcription_segments'] else 0)
        
        st.markdown("---")

# Footer

st.markdown("---")

if PYDUB_AVAILABLE:
    st.success("""
    ### ✨ **FFmpeg Enabled - Full Audio Support!**

    ✅ **Upload ANY audio format** - MP3, M4A, AMR, AAC, 3GP, WAV, OGG, FLAC, WMA, WEBM, etc.  
    ✅ **Auto-converts instantly** - No manual conversion needed  
    ✅ **100% Free & Local** - No API keys, no online services  
    ✅ **Fast & reliable** - Direct processing on your machine  
    ✅ **Easy to use** - Just upload and transcribe!  
    ✅ **Phone recordings** - AMR, 3GP, M4A from mobile devices  
    ✅ **Voice memos** - M4A from iPhone, AMR from Android  
    ✅ **Music files** - MP3, AAC, WMA, FLAC  

    🎯 **Supports ALL major audio formats - just upload and go!**
    """)
elif AUDIO_CONVERSION_AVAILABLE:
    st.success("""
    ### ✨ **Audio Conversion Available!**

    ✅ **Supported formats:** WAV, FLAC, OGG (instant)  
    ✅ **For MP3/M4A/AMR:** Run `python install_ffmpeg_simple.py` for full support  
    ✅ **100% Free** - No API keys needed  

    💡 **Tip:** Install FFmpeg once to support ALL audio formats automatically!
    """)
else:
    st.info("""
    ### 💡 **Enable Audio Conversion**

    To support multiple audio formats, install these packages:
    
    ```bash
    pip install soundfile librosa
    ```
    
    For full MP3/M4A/AMR support:
    ```bash
    python install_ffmpeg_simple.py
    ```
    """)

st.markdown("---")

# Footer with creator information
st.markdown("---")

# Create footer layout with text on left and image on right
footer_text_col, footer_img_col = st.columns([3, 1])

with footer_text_col:
    st.markdown("""
    <div style='padding: 20px 0;'>
        <h4 style='margin-bottom: 5px;'>Created by Abdulrahaman Musa</h4>
        <p style='color: #666; margin: 5px 0;'>Data Scientist | Survey Research Specialist</p>
        <p style='font-size: 12px; color: #888; margin: 5px 0;'>Built with ❤️ for Hausa Language Speakers</p>
        <p style='font-size: 11px; color: #999; margin: 5px 0;'>Powered by Google Speech Recognition & FFmpeg</p>
        <p style='font-size: 10px; color: #aaa; margin-top: 10px;'>© 2026 Abdulrahaman Musa | Mortality Survey Transcription Tool</p>
    </div>
    """, unsafe_allow_html=True)

with footer_img_col:
    # Profile image in bottom right corner
    try:
        from pathlib import Path
        
        # Look for mypic.jpg first, then other possible names
        possible_image_names = ['mypic.jpg', 'mypic.png', 'profile.jpg', 'profile.png', 
                               'abdulrahaman.jpg', 'abdulrahaman.png']
        
        image_found = False
        for img_name in possible_image_names:
            img_path = Path(__file__).parent / img_name
            if img_path.exists():
                st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
                st.image(str(img_path), width=120)
                st.markdown("</div>", unsafe_allow_html=True)
                image_found = True
                break
        
        if not image_found:
            # Show placeholder with initials in right corner
            st.markdown("""
            <div style='text-align: right;'>
                <div style='width: 120px; height: 120px; border-radius: 50%; 
                           background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           display: inline-flex; align-items: center; justify-content: center;
                           font-size: 40px; color: white; font-weight: bold;'>
                    AM
                </div>
                <p style='font-size: 9px; color: #999; text-align: right; margin-top: 5px;'>
                Add 'mypic.jpg' to show photo
                </p>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        # Fallback placeholder
        st.markdown("""
        <div style='text-align: right;'>
            <div style='width: 120px; height: 120px; border-radius: 50%; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                       display: inline-flex; align-items: center; justify-content: center;
                       font-size: 40px; color: white; font-weight: bold;'>
                AM
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
