#!/usr/bin/env python3
"""Test script to directly test GCP Speech-to-Text API."""
import os
import base64
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GCP_API_KEY = os.getenv("GCP_API_KEY")

if not GCP_API_KEY:
    print("❌ GCP_API_KEY not found in environment")
    exit(1)

print(f"✅ GCP API Key found (length: {len(GCP_API_KEY)})")
print(f"   Key starts with: {GCP_API_KEY[:10]}...")

# Create a simple test audio (WAV format - "Hello" in PCM format)
# This is a minimal valid WAV file with silence
# For a real test, we'd need actual audio data
print("\n📝 Testing GCP Speech-to-Text API...")

# Test 1: Try with a minimal valid WAV file (silence)
# WAV header + minimal PCM data
wav_header = b'RIFF'
wav_data = b'RIFF' + (36).to_bytes(4, 'little') + b'WAVE' + b'fmt ' + (16).to_bytes(4, 'little') + \
           (1).to_bytes(2, 'little') + (1).to_bytes(2, 'little') + (16000).to_bytes(4, 'little') + \
           (32000).to_bytes(4, 'little') + (2).to_bytes(2, 'little') + (16).to_bytes(2, 'little') + \
           b'data' + (0).to_bytes(4, 'little')

audio_content = base64.b64encode(wav_data).decode('utf-8')

url = f"https://speech.googleapis.com/v1/speech:recognize?key={GCP_API_KEY}"

# Test with auto-detection
print("\n🧪 Test 1: Auto-detection (ENCODING_UNSPECIFIED)")
payload1 = {
    "config": {
        "languageCode": "en-US",
        "enableAutomaticPunctuation": True
    },
    "audio": {
        "content": audio_content
    }
}

try:
    response1 = requests.post(url, json=payload1, timeout=15)
    print(f"   Status Code: {response1.status_code}")
    if response1.status_code == 200:
        result = response1.json()
        print(f"   ✅ Success! Response: {json.dumps(result, indent=2)}")
    else:
        print(f"   ❌ Error Response: {response1.text}")
        try:
            error_json = response1.json()
            print(f"   Error Details: {json.dumps(error_json, indent=2)}")
        except:
            pass
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 2: Try with LINEAR16 encoding
print("\n🧪 Test 2: LINEAR16 encoding, 16kHz")
payload2 = {
    "config": {
        "encoding": "LINEAR16",
        "sampleRateHertz": 16000,
        "languageCode": "en-US",
        "enableAutomaticPunctuation": True
    },
    "audio": {
        "content": audio_content
    }
}

try:
    response2 = requests.post(url, json=payload2, timeout=15)
    print(f"   Status Code: {response2.status_code}")
    if response2.status_code == 200:
        result = response2.json()
        print(f"   ✅ Success! Response: {json.dumps(result, indent=2)}")
    else:
        print(f"   ❌ Error Response: {response2.text}")
        try:
            error_json = response2.json()
            print(f"   Error Details: {json.dumps(error_json, indent=2)}")
        except:
            pass
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test 3: Check if API key is valid by testing a simple endpoint
print("\n🧪 Test 3: Verify API key validity")
test_url = f"https://speech.googleapis.com/v1/projects?key={GCP_API_KEY}"
try:
    # This might fail but will tell us if the key is valid
    test_response = requests.get(test_url, timeout=10)
    print(f"   Status Code: {test_response.status_code}")
    if test_response.status_code == 200:
        print("   ✅ API key appears to be valid")
    elif test_response.status_code == 403:
        print("   ⚠️  API key might not have proper permissions")
        print(f"   Response: {test_response.text[:200]}")
    elif test_response.status_code == 401:
        print("   ❌ API key is invalid")
    else:
        print(f"   Response: {test_response.text[:200]}")
except Exception as e:
    print(f"   ⚠️  Could not verify API key: {e}")

print("\n" + "="*60)
print("💡 Note: Empty audio will return empty results, which is expected.")
print("   The important thing is whether we get 200 (success) or 400 (error).")

