"""Streamlit UI for Credit Card Assistant."""
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import requests
import base64
import json
from datetime import datetime
import os

# Configuration
PYTHON_API_URL = os.getenv("PYTHON_API_URL", "http://localhost:8000")
NODE_API_URL = os.getenv("NODE_API_URL", "http://localhost:3000")

# Page configuration
st.set_page_config(
    page_title="Credit Card Assistant",
    page_icon="💳",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_info" not in st.session_state:
    st.session_state.user_info = None
if "pending_consent" not in st.session_state:
    st.session_state.pending_consent = None
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None
if "last_processed_message" not in st.session_state:
    st.session_state.last_processed_message = None
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False


def login_user(email: str, password: str):
    """Login user and get access token."""
    try:
        response = requests.post(
            f"{PYTHON_API_URL}/auth/login",
            json={"email": email, "password": password},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return {"success": False, "error": "Invalid email or password"}
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def signup_user(name: str, email: str, phone: str, password: str):
    """Sign up new user."""
    try:
        response = requests.post(
            f"{PYTHON_API_URL}/auth/signup",
            json={"name": name, "email": email, "phone": phone, "password": password},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            error_detail = e.response.json().get("detail", "User already exists")
            return {"success": False, "error": error_detail}
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_chat_message(message: str):
    """Send chat message to Python backend."""
    try:
        headers = {}
        if st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        response = requests.post(
            f"{PYTHON_API_URL}/chat",
            params={"message": message},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.session_state.user_id = None
            return {"success": False, "error": "Session expired. Please login again."}
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_voice_message(audio_bytes: bytes):
    """Send voice message to Python backend."""
    try:
        if not audio_bytes or len(audio_bytes) == 0:
            return {"success": False, "error": "No audio data provided"}
        
        audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        headers = {}
        if st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        response = requests.post(
            f"{PYTHON_API_URL}/voice",
            json={"audio_data": audio_b64},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        # Debug logging
        if not result.get("success"):
            print(f"Voice API error: {result.get('error')}")
        
        return result
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.session_state.user_id = None
            return {"success": False, "error": "Session expired. Please login again."}
        return {"success": False, "error": str(e)}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out. The audio might be too long or the server is slow."}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Could not connect to backend. Is the Python backend running on port 8000?"}
    except Exception as e:
        return {"success": False, "error": f"Error sending voice message: {str(e)}"}


def handle_consent(consent: bool, action: str, action_params: dict = None):
    """Handle user consent for action execution."""
    try:
        headers = {}
        if st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        response = requests.post(
            f"{PYTHON_API_URL}/consent",
            json={
                "query_id": f"Q{datetime.now().timestamp()}",
                "user_id": st.session_state.user_id,
                "consent": consent,
                "action": action,
                "action_params": action_params or {}
            },
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.session_state.user_id = None
            return {"success": False, "error": "Session expired. Please login again."}
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Authentication check
if not st.session_state.access_token:
    # Show login/signup page
    st.title("💳 Credit Card Assistant")
    st.markdown("### Please login or sign up to continue")
    
    if st.session_state.show_signup:
        st.subheader("Sign Up")
        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="John Doe")
            email = st.text_input("Email", placeholder="john@example.com")
            phone = st.text_input("Phone Number", placeholder="+919876543210")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit_signup = st.form_submit_button("Sign Up", use_container_width=True)
            with col2:
                back_to_login = st.form_submit_button("Back to Login", use_container_width=True)
            
            if submit_signup:
                if not all([name, email, phone, password, confirm_password]):
                    st.error("Please fill in all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    result = signup_user(name, email, phone, password)
                    if result.get("success"):
                        st.session_state.access_token = result.get("access_token")
                        st.session_state.user_info = result.get("user")
                        st.session_state.user_id = result.get("user", {}).get("user_id")
                        st.session_state.show_signup = False
                        st.success("Sign up successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error(result.get("error", "Sign up failed"))
            
            if back_to_login:
                st.session_state.show_signup = False
                st.rerun()
    else:
        st.subheader("Login")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="john@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit_login = st.form_submit_button("Login", use_container_width=True, type="primary")
            with col2:
                show_signup = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submit_login:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    result = login_user(email, password)
                    if result.get("success"):
                        st.session_state.access_token = result.get("access_token")
                        st.session_state.user_info = result.get("user")
                        st.session_state.user_id = result.get("user", {}).get("user_id")
                        st.success("Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error(result.get("error", "Login failed"))
            
            if show_signup:
                st.session_state.show_signup = True
                st.rerun()
    
    st.stop()

# Main UI (only shown if authenticated)
st.title("💳 Credit Card Assistant")
st.markdown("Ask me anything about your credit card account!")

# Sidebar
with st.sidebar:
    st.header("Account")
    if st.session_state.user_info:
        st.markdown(f"**Name:** {st.session_state.user_info.get('name', 'N/A')}")
        st.markdown(f"**Email:** {st.session_state.user_info.get('email', 'N/A')}")
        st.markdown(f"**User ID:** {st.session_state.user_info.get('user_id', 'N/A')}")
    
    st.markdown("---")
    st.markdown("### Query Categories")
    st.markdown("""
    - 💳 Account & Onboarding
    - 🚚 Card Delivery
    - 💰 Transaction & EMI
    - 📄 Bill & Statement
    - 💸 Repayments
    - 🚨 Collections
    """)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Chat", type="secondary", use_container_width=True):
            # Clear all chat-related session state
            st.session_state.messages = []
            st.session_state.pending_consent = None
            st.session_state.last_processed_message = None
            st.session_state.last_processed_audio = None
            # Force rerun to update the UI
            st.rerun()
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.access_token = None
            st.session_state.user_info = None
            st.session_state.user_id = None
            st.session_state.messages = []
            st.session_state.pending_consent = None
            st.rerun()

# Display chat messages
if st.session_state.messages:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show classification if available
            if "classification" in message:
                with st.expander("🔍 Classification Details"):
                    st.json(message["classification"])
            
            # Show data if available
            if "data" in message and message["data"]:
                with st.expander("📊 Response Data"):
                    st.json(message["data"])
else:
    # Show welcome message when chat is empty
    with st.chat_message("assistant"):
        st.markdown("👋 Hello! I'm your Credit Card Assistant. How can I help you today?")
        st.markdown("You can ask me about:")
        st.markdown("- 💳 Account balance and details")
        st.markdown("- 🚚 Card delivery status")
        st.markdown("- 💰 Transactions and EMI")
        st.markdown("- 📄 Bills and statements")
        st.markdown("- 💸 Repayments")
        st.markdown("- 🚨 Collections")

# Handle pending consent
if st.session_state.pending_consent:
    st.warning("⚠️ Action requires your consent")
    consent_info = st.session_state.pending_consent
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve", type="primary", use_container_width=True):
            result = handle_consent(
                True,
                consent_info["action"],
                consent_info.get("action_params")
            )
            
            if result.get("success"):
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"✅ {result.get('message', 'Action completed successfully')}",
                    "data": result.get("data")
                })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Error: {result.get('message', 'Action failed')}"
                })
            
            st.session_state.pending_consent = None
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.messages.append({
                "role": "assistant",
                "content": "❌ Action cancelled by user"
            })
            st.session_state.pending_consent = None
            st.rerun()
    
    st.info(f"**Action:** {consent_info.get('action', 'N/A')}\n\n**Message:** {consent_info.get('consent_message', '')}")

# Chat input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Check if we've already processed this message to prevent loops
    if user_input != st.session_state.get("last_processed_message"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Mark as processed before sending to prevent race conditions
        st.session_state.last_processed_message = user_input
        
        # Send to backend
        with st.spinner("Processing..."):
            result = send_chat_message(user_input)
        
        if result.get("success"):
            response_data = result.get("response", {})
            answer = response_data.get("answer", "No response")
            classification = result.get("classification", {})
            
            # Check if consent is required
            if response_data.get("requires_consent"):
                st.session_state.pending_consent = {
                    "action": response_data.get("action"),
                    "consent_message": response_data.get("consent_message", ""),
                    "action_params": response_data.get("action_params") or {}
                }
                answer += f"\n\n⚠️ **{response_data.get('consent_message', 'Action requires your consent')}**"
            
            # Add assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "classification": classification,
                "data": response_data.get("data")
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Error: {result.get('error', 'Unknown error')}"
            })
        
        st.rerun()

# Voice input section
st.markdown("---")
st.subheader("🎤 Voice Input")

audio_bytes = None

# Audio recorder with button
st.write("Click the microphone button below to record your voice message:")
audio_bytes = audio_recorder(
    text="🎤 Click to record",
    recording_color="#e8b4c8",
    neutral_color="#6aa36f",
    icon_name="microphone",
    icon_size="2x",
    pause_threshold=2.0
)

# Debug: Show what we got from the recorder
if audio_bytes:
    # The audio_recorder returns bytes directly
    if isinstance(audio_bytes, bytes):
        st.caption(f"📊 Audio received: {len(audio_bytes)} bytes")
    else:
        st.caption(f"📊 Audio type: {type(audio_bytes)}")

# If audio was recorded, process it
if audio_bytes:
    # Convert to bytes if it's not already
    if isinstance(audio_bytes, dict):
        audio_bytes = audio_bytes.get('bytes', b'')
    
    # Ensure we have bytes
    if isinstance(audio_bytes, str):
        audio_bytes = audio_bytes.encode('latin-1')
    
    # Check if we've already processed this audio to prevent loops
    if audio_bytes and len(audio_bytes) > 0 and audio_bytes != st.session_state.get("last_processed_audio"):
        # Show audio info for debugging
        st.info(f"🎤 Audio recorded: {len(audio_bytes)} bytes")
        
        with st.spinner("Transcribing and processing..."):
            try:
                result = send_voice_message(audio_bytes)
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")
                st.stop()
        
        # Always show the result, even if there's an error
        if result.get("success"):
            transcript = result.get("transcript", "")
            response_data = result.get("response", {})
            answer = response_data.get("answer", "No response")
            classification = result.get("classification", {})
            
            if transcript:
                # Show transcript
                st.success(f"📝 **Transcribed:** {transcript}")
                
                # Check if consent is required
                if response_data.get("requires_consent"):
                    st.session_state.pending_consent = {
                        "action": response_data.get("action"),
                        "consent_message": response_data.get("consent_message", ""),
                        "action_params": response_data.get("action_params") or {}
                    }
                    answer += f"\n\n⚠️ **{response_data.get('consent_message', 'Action requires your consent')}**"
                
                # Add messages
                st.session_state.messages.append({
                    "role": "user",
                    "content": transcript
                })
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "classification": classification,
                    "data": response_data.get("data")
                })
            else:
                st.warning("⚠️ Audio was processed but no transcript was returned. The audio might be too short, silent, or unclear. Please try recording again.")
                # Add error message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "⚠️ I couldn't transcribe your audio. Please try speaking more clearly or use text input instead."
                })
        else:
            error_msg = result.get('error', 'Failed to process voice input')
            debug_info = result.get('debug_info', {})
            
            st.error(f"❌ **Error:** {error_msg}")
            
            # Show debugging info
            with st.expander("🔍 Debug Information"):
                st.write(f"**Audio size:** {len(audio_bytes)} bytes")
                st.write(f"**Backend URL:** {PYTHON_API_URL}")
                st.write(f"**Error details:** {error_msg}")
                if debug_info:
                    st.write(f"**GCP Available:** {debug_info.get('gcp_available', 'Unknown')}")
                    st.write(f"**GCP API Key Set:** {debug_info.get('gcp_api_key_set', 'Unknown')}")
                st.write("**Troubleshooting:**")
                st.write("1. Check if Python backend is running on port 8000")
                st.write("2. Verify GCP API key is set in .env file")
                st.write("3. Ensure Speech-to-Text API is enabled in GCP")
                st.write("4. Try recording a longer audio (3-5 seconds)")
                st.write("5. Speak clearly and ensure microphone permissions are granted")
            
            # Add error message to chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ **Error processing voice input:** {error_msg}\n\nPlease try recording again or use text input."
            })
        
        # Mark this audio as processed to prevent reprocessing
        st.session_state.last_processed_audio = audio_bytes
        st.rerun()

# Fallback: File uploader for audio files
st.markdown("---")
st.write("**Or upload an audio file:**")
uploaded_audio = st.file_uploader(
    "Upload an audio file (WAV, MP3, M4A, etc.)",
    type=['wav', 'mp3', 'm4a', 'ogg', 'flac', 'webm'],
    key="audio_upload",
    help="Upload an audio file to convert speech to text"
)

if uploaded_audio:
    audio_bytes = uploaded_audio.read()
    # Check if we've already processed this audio
    if audio_bytes != st.session_state.get("last_processed_audio"):
        with st.spinner("Transcribing and processing..."):
            result = send_voice_message(audio_bytes)
        
        if result.get("success"):
            transcript = result.get("transcript", "")
            response_data = result.get("response", {})
            answer = response_data.get("answer", "No response")
            classification = result.get("classification", {})
            
            st.success(f"📝 **Transcribed:** {transcript}")
            
            if response_data.get("requires_consent"):
                st.session_state.pending_consent = {
                    "action": response_data.get("action"),
                    "consent_message": response_data.get("consent_message", ""),
                    "action_params": response_data.get("action_params") or {}
                }
                answer += f"\n\n⚠️ **{response_data.get('consent_message', 'Action requires your consent')}**"
            
            st.session_state.messages.append({
                "role": "user",
                "content": transcript
            })
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "classification": classification,
                "data": response_data.get("data")
            })
            
            # Mark this audio as processed
            st.session_state.last_processed_audio = audio_bytes
        else:
            st.error(f"Error: {result.get('error', 'Failed to process voice input')}")
        
        st.rerun()

# Footer
st.markdown("---")
st.markdown("**Credit Card Assistant** | Built with FastAPI, Streamlit, and OpenAI")

