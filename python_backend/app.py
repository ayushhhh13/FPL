"""Main FastAPI application for credit card assistant."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from database.db import get_db, init_db
from classifier import QueryClassifier
from utils.speech_to_text import SpeechToText
from agents.account_agent import AccountAgent
from agents.delivery_agent import DeliveryAgent
from agents.transaction_agent import TransactionAgent
from agents.bill_agent import BillAgent
from agents.repayment_agent import RepaymentAgent
from agents.collections_agent import CollectionsAgent

load_dotenv()

app = FastAPI(title="Credit Card Assistant API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
classifier = QueryClassifier()
speech_to_text = SpeechToText()

# Agent mapping
AGENT_MAP = {
    "account": AccountAgent,
    "delivery": DeliveryAgent,
    "transaction": TransactionAgent,
    "bill": BillAgent,
    "repayment": RepaymentAgent,
    "collections": CollectionsAgent
}


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str
    user_id: str = "USER001"  # Default user for demo


class VoiceRequest(BaseModel):
    """Voice request model."""
    audio_data: str  # Base64 encoded audio
    user_id: str = "USER001"


class ConsentRequest(BaseModel):
    """Consent request model."""
    query_id: str
    user_id: str
    consent: bool
    action: str
    action_params: Optional[dict] = None


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Credit Card Assistant API", "status": "running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    assemblyai_available = speech_to_text.available if hasattr(speech_to_text, 'available') else False
    return {
        "status": "healthy",
        "speech_to_text_service": "AssemblyAI",
        "assemblyai_available": assemblyai_available,
        "assemblyai_api_key_set": bool(os.getenv("ASSEMBLYAI_API_KEY"))
    }


@app.post("/classify")
async def classify_query(request: ChatRequest):
    """
    Classify a user query into category and task type.
    
    Args:
        request: Chat request with message and user_id
        
    Returns:
        Classification result
    """
    try:
        classification = classifier.classify(request.message)
        return {
            "success": True,
            "classification": classification,
            "query": request.message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: ChatRequest, db=Depends(get_db)):
    """
    Process chat message and return response.
    
    Args:
        request: Chat request with message and user_id
        db: Database session
        
    Returns:
        Response from appropriate agent
    """
    try:
        # Classify query
        classification = classifier.classify(request.message)
        category = classification["category"]
        task_type = classification["task_type"]
        
        # Get appropriate agent
        AgentClass = AGENT_MAP.get(category, AccountAgent)
        agent = AgentClass(db)
        
        # Process query
        response = agent.process(request.message, request.user_id, task_type)
        
        return {
            "success": True,
            "response": response,
            "classification": classification
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice")
async def voice(request: VoiceRequest, db=Depends(get_db)):
    """
    Process voice input and return response.
    
    Args:
        request: Voice request with audio data and user_id
        db: Database session
        
    Returns:
        Response from appropriate agent
    """
    try:
        import base64
        
        # Decode audio data
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Convert speech to text
        print(f"🎤 Received voice input - audio size: {len(audio_bytes)} bytes")
        transcript = speech_to_text.transcribe_audio_bytes(audio_bytes)
        
        if not transcript:
            # Log more details for debugging
            print(f"❌ Audio transcription failed. Audio size: {len(audio_bytes)} bytes")
            print(f"   GCP API Key present: {bool(os.getenv('GCP_API_KEY'))}")
            print(f"   Speech-to-text available: {speech_to_text.available}")
            print(f"   Using REST API: {speech_to_text.use_rest_api if hasattr(speech_to_text, 'use_rest_api') else 'Unknown'}")
            
            # Check for specific error messages from transcription
            error_msg = "Could not transcribe audio."
            
            # Check if audio is too small (likely empty or invalid)
            if len(audio_bytes) < 1000:
                error_msg = "Audio file is too small. Please record a longer message (at least 2-3 seconds)."
            else:
                # Check logs for billing error (this would be in the transcription function)
                # For now, provide a general message that includes billing as a possibility
                error_msg = "Could not transcribe audio. Common causes: 1) GCP billing not enabled (most common), 2) Audio format not supported, 3) Audio contains only silence, 4) Network connectivity issues. Please check GCP billing status or use text input instead."
            
            return {
                "success": False,
                "error": error_msg,
                "debug_info": {
                    "audio_size": len(audio_bytes),
                    "gcp_available": speech_to_text.available,
                    "gcp_api_key_set": bool(os.getenv('GCP_API_KEY')),
                    "audio_too_small": len(audio_bytes) < 1000,
                    "note": "If you see this error repeatedly, check if GCP billing is enabled for your project"
                }
            }
        
        # Classify query
        classification = classifier.classify(transcript)
        category = classification["category"]
        task_type = classification["task_type"]
        
        # Get appropriate agent
        AgentClass = AGENT_MAP.get(category, AccountAgent)
        agent = AgentClass(db)
        
        # Process query
        response = agent.process(transcript, request.user_id, task_type)
        
        return {
            "success": True,
            "transcript": transcript,
            "response": response,
            "classification": classification
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/consent")
async def handle_consent(request: ConsentRequest, db=Depends(get_db)):
    """
    Handle user consent for action execution.
    
    Args:
        request: Consent request with user decision
        db: Database session
        
    Returns:
        Action execution result
    """
    try:
        import requests
        node_api_url = os.getenv("NODE_API_URL", "http://localhost:3000")
        
        if not request.consent:
            return {
                "success": False,
                "message": "Action cancelled by user"
            }
        
        # Call Node.js API for action execution
        action_params = request.action_params or {}
        action_params["user_id"] = request.user_id
        
        # Map actions to API endpoints
        api_endpoints = {
            "make_payment": f"{node_api_url}/api/transactions",
            "update_email": f"{node_api_url}/api/update-user",
            "update_phone": f"{node_api_url}/api/update-user",
            "update_profile": f"{node_api_url}/api/update-user",
            "activate_card": f"{node_api_url}/api/update-user",
            "block_card": f"{node_api_url}/api/update-user",
            "unblock_card": f"{node_api_url}/api/update-user",
            "dispute_transaction": f"{node_api_url}/api/transactions",
            "convert_to_emi": f"{node_api_url}/api/transactions"
        }
        
        endpoint = api_endpoints.get(request.action, f"{node_api_url}/api/transactions")
        
        try:
            api_response = requests.post(endpoint, json=action_params, timeout=5)
            api_response.raise_for_status()
            
            return {
                "success": True,
                "message": f"Action '{request.action}' executed successfully",
                "data": api_response.json()
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Error executing action: {str(e)}"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

