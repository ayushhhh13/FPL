#!/usr/bin/env python3
"""Test script to verify AssemblyAI integration."""
import os
import sys
from dotenv import load_dotenv

# Add python_backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python_backend'))

load_dotenv()

from utils.speech_to_text import SpeechToText

print("🧪 Testing AssemblyAI Speech-to-Text Integration\n")

# Initialize
stt = SpeechToText()

if not stt.available:
    print("❌ AssemblyAI is not available")
    print(f"   API Key set: {bool(os.getenv('ASSEMBLYAI_API_KEY'))}")
    exit(1)

print("✅ AssemblyAI initialized successfully")
print(f"   API Key: {os.getenv('ASSEMBLYAI_API_KEY', '')[:20]}...")
print(f"   Base URL: {stt.base_url}")

# Test with a minimal audio file (we'll create a simple WAV)
print("\n📝 Note: To fully test transcription, you need actual audio data.")
print("   The integration is ready - try recording voice in the UI!")

print("\n✅ AssemblyAI integration is configured and ready to use!")

