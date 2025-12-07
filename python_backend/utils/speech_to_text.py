"""AssemblyAI Speech-to-Text integration."""
import os
import base64
import requests
import time
from dotenv import load_dotenv

load_dotenv()


class SpeechToText:
    """Handle speech-to-text conversion using AssemblyAI."""
    
    def __init__(self):
        """Initialize AssemblyAI client."""
        self.api_key = os.getenv("ASSEMBLYAI_API_KEY")
        
        if self.api_key:
            self.available = True
            self.base_url = "https://api.assemblyai.com/v2"
            self.headers = {
                "authorization": self.api_key,
                "content-type": "application/json"
            }
            print("✅ Using AssemblyAI Speech-to-Text API")
        else:
            print("⚠️  Warning: AssemblyAI API key not found. Speech-to-text will not be available.")
            self.available = False
            self.base_url = None
            self.headers = None
    
    def transcribe_audio_file(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        if not self.available:
            return ""
        
        try:
            with open(audio_file_path, "rb") as audio_file:
                audio_bytes = audio_file.read()
            return self.transcribe_audio_bytes(audio_bytes)
        except Exception as e:
            print(f"Error reading audio file: {e}")
            return ""
    
    def transcribe_audio_bytes(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio bytes to text using AssemblyAI.
        
        Args:
            audio_bytes: Audio data as bytes
            
        Returns:
            Transcribed text
        """
        if not self.available:
            return ""
        
        if not audio_bytes or len(audio_bytes) < 100:
            print("⚠️  Audio too short or empty")
            return ""
        
        try:
            print(f"🎤 Starting AssemblyAI transcription - input audio size: {len(audio_bytes)} bytes")
            
            # Step 1: Upload audio file to AssemblyAI
            upload_url = f"{self.base_url}/upload"
            upload_response = requests.post(
                upload_url,
                headers={"authorization": self.api_key},
                data=audio_bytes,
                timeout=30
            )
            
            if upload_response.status_code != 200:
                error_msg = f"Failed to upload audio: {upload_response.status_code} - {upload_response.text}"
                print(f"❌ {error_msg}")
                return ""
            
            upload_data = upload_response.json()
            audio_url = upload_data.get("upload_url")
            
            if not audio_url:
                print("❌ No upload URL returned from AssemblyAI")
                return ""
            
            print(f"✅ Audio uploaded successfully. URL: {audio_url[:50]}...")
            
            # Step 2: Submit transcription request
            transcript_endpoint = f"{self.base_url}/transcript"
            transcript_request = {
                "audio_url": audio_url,
                "language_code": "en_us",
                "punctuate": True,
                "format_text": True
            }
            
            transcript_response = requests.post(
                transcript_endpoint,
                json=transcript_request,
                headers=self.headers,
                timeout=15
            )
            
            if transcript_response.status_code != 200:
                error_msg = f"Failed to submit transcription: {transcript_response.status_code} - {transcript_response.text}"
                print(f"❌ {error_msg}")
                return ""
            
            transcript_data = transcript_response.json()
            transcript_id = transcript_data.get("id")
            
            if not transcript_id:
                print("❌ No transcript ID returned")
                return ""
            
            print(f"✅ Transcription submitted. ID: {transcript_id}")
            
            # Step 3: Poll for transcription result
            polling_endpoint = f"{self.base_url}/transcript/{transcript_id}"
            max_attempts = 30  # 30 attempts * 2 seconds = 60 seconds max
            attempt = 0
            
            while attempt < max_attempts:
                polling_response = requests.get(
                    polling_endpoint,
                    headers=self.headers,
                    timeout=15
                )
                
                if polling_response.status_code != 200:
                    error_msg = f"Failed to poll transcription: {polling_response.status_code} - {polling_response.text}"
                    print(f"❌ {error_msg}")
                    return ""
                
                polling_data = polling_response.json()
                status = polling_data.get("status")
                
                if status == "completed":
                    transcript = polling_data.get("text", "")
                    if transcript:
                        print(f"✅ Transcription completed: {transcript[:50]}...")
                        return transcript.strip()
                    else:
                        print("⚠️  Transcription completed but no text returned")
                        return ""
                elif status == "error":
                    error_msg = polling_data.get("error", "Unknown error")
                    print(f"❌ Transcription error: {error_msg}")
                    return ""
                elif status in ["queued", "processing"]:
                    attempt += 1
                    if attempt % 5 == 0:  # Log every 5 attempts
                        print(f"⏳ Transcription {status}... (attempt {attempt}/{max_attempts})")
                    time.sleep(2)  # Wait 2 seconds before next poll
                else:
                    print(f"⚠️  Unknown status: {status}")
                    attempt += 1
                    time.sleep(2)
            
            print("❌ Transcription timeout - took too long to complete")
            return ""
            
        except requests.exceptions.Timeout:
            print("❌ Request timeout - AssemblyAI API took too long to respond")
            return ""
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return ""
        except Exception as e:
            print(f"❌ Error in AssemblyAI transcription: {e}")
            import traceback
            traceback.print_exc()
            return ""
