"""Main FastAPI application for credit card assistant."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

from database.db import get_db, init_db
from database.models import User, Transaction
from classifier import QueryClassifier
from utils.speech_to_text import SpeechToText
from utils.auth import hash_password, verify_password, create_access_token, decode_access_token
from utils.email_service import GmailService
from utils.whatsapp_service import WhatsAppService
from agents.account_agent import AccountAgent
from agents.delivery_agent import DeliveryAgent
from agents.transaction_agent import TransactionAgent
from agents.bill_agent import BillAgent
from agents.repayment_agent import RepaymentAgent
from agents.collections_agent import CollectionsAgent
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Header
import re
import uuid

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
email_service = GmailService()
whatsapp_service = WhatsAppService()
security = HTTPBearer()

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
    """Chat request model (for classify endpoint)."""
    message: str


class VoiceRequest(BaseModel):
    """Voice request model."""
    audio_data: str  # Base64 encoded audio


class ConsentRequest(BaseModel):
    """Consent request model."""
    query_id: str
    user_id: str
    consent: bool
    action: str
    action_params: Optional[dict] = None


class SignupRequest(BaseModel):
    """Signup request model."""
    name: str
    email: str
    phone: str
    password: str


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user


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
        "assemblyai_api_key_set": bool(os.getenv("ASSEMBLYAI_API_KEY")),
        "gmail_service_available": email_service.use_api,
        "whatsapp_service_available": whatsapp_service.use_api,
        "email_save_to_file": True,
        "whatsapp_save_to_file": True
    }


@app.post("/auth/signup")
async def signup(request: SignupRequest, db=Depends(get_db)):
    """
    User signup endpoint.
    
    Args:
        request: Signup request with name, email, phone, password
        db: Database session
        
    Returns:
        User info and access token
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == request.email) | (User.phone == request.phone)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="User with this email or phone already exists"
            )
        
        # Generate user_id
        user_id = f"USER{str(uuid.uuid4())[:8].upper()}"
        
        # Create new user
        new_user = User(
            user_id=user_id,
            name=request.name,
            email=request.email,
            phone=request.phone,
            password_hash=hash_password(request.password),
            card_number=f"CARD{str(uuid.uuid4())[:12].upper()}",
            card_status="active",
            credit_limit=100000.0,
            available_credit=100000.0,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access token
        access_token = create_access_token(data={"sub": user_id})
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "user_id": new_user.user_id,
                "name": new_user.name,
                "email": new_user.email,
                "phone": new_user.phone
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error during signup: {str(e)}")


@app.post("/auth/login")
async def login(request: LoginRequest, db=Depends(get_db)):
    """
    User login endpoint.
    
    Args:
        request: Login request with email and password
        db: Database session
        
    Returns:
        User info and access token
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        
        if not user or not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="Account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token = create_access_token(data={"sub": user.user_id})
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")


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
async def chat(
    message: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Process chat message and return response.
    
    Args:
        message: Chat message
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Response from appropriate agent
    """
    try:
        # Classify query
        classification = classifier.classify(message)
        category = classification["category"]
        task_type = classification["task_type"]
        
        # Get appropriate agent
        AgentClass = AGENT_MAP.get(category, AccountAgent)
        agent = AgentClass(db)
        
        # Process query
        response = agent.process(message, current_user.user_id, task_type)
        
        # Send chat summary to email (async, don't wait for response)
        try:
            chat_messages = [
                {"role": "user", "content": message},
                {"role": "assistant", "content": response.get("answer", "No response")}
            ]
            email_service.send_chat_summary(
                current_user.email,
                current_user.name,
                chat_messages
            )
        except Exception as e:
            print(f"⚠️ Failed to send email: {str(e)}")
        
        return {
            "success": True,
            "response": response,
            "classification": classification
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voice")
async def voice(
    request: VoiceRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Process voice input and return response.
    
    Args:
        request: Voice request with audio data
        current_user: Authenticated user
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
            print(f"   Speech-to-text available: {speech_to_text.available}")
            
            error_msg = "Could not transcribe audio."
            if len(audio_bytes) < 1000:
                error_msg = "Audio file is too small. Please record a longer message (at least 2-3 seconds)."
            
            return {
                "success": False,
                "error": error_msg,
                "debug_info": {
                    "audio_size": len(audio_bytes),
                    "assemblyai_available": speech_to_text.available,
                    "audio_too_small": len(audio_bytes) < 1000
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
        response = agent.process(transcript, current_user.user_id, task_type)
        
        # Send chat summary to email (async, don't wait for response)
        try:
            chat_messages = [
                {"role": "user", "content": f"[Voice] {transcript}"},
                {"role": "assistant", "content": response.get("answer", "No response")}
            ]
            email_service.send_chat_summary(
                current_user.email,
                current_user.name,
                chat_messages
            )
        except Exception as e:
            print(f"⚠️ Failed to send email: {str(e)}")
        
        return {
            "success": True,
            "transcript": transcript,
            "response": response,
            "classification": classification
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/consent")
async def handle_consent(
    request: ConsentRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Handle user consent for action execution.
    
    Args:
        request: Consent request with user decision
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Action execution result
    """
    try:
        import requests
        node_api_url = os.getenv("NODE_API_URL", "http://localhost:3000")
        
        # Verify user_id matches authenticated user
        if request.user_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="User ID mismatch")
        
        if not request.consent:
            return {
                "success": False,
                "message": "Action cancelled by user"
            }
        
        # Check card status before allowing transactions/payments
        if request.action in ["make_payment", "make_transaction"]:
            if current_user.card_status == "blocked":
                return {
                    "success": False,
                    "message": "❌ Transaction failed: Your card is currently blocked. Please unblock your card first to make transactions."
                }
        
        # Call Node.js API for action execution
        action_params = request.action_params or {}
        action_params["user_id"] = current_user.user_id
        action_params["action"] = request.action
        
        # Map actions to API endpoints
        api_endpoints = {
            "make_payment": f"{node_api_url}/api/transactions",
            "make_transaction": f"{node_api_url}/api/transactions",
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
            api_data = api_response.json()
            
            # Update database for block/unblock actions
            if request.action in ["block_card", "unblock_card", "activate_card"]:
                if "card_status" in api_data:
                    current_user.card_status = api_data["card_status"]
                    db.commit()
                    print(f"✅ Updated card status to '{api_data['card_status']}' for user {current_user.user_id}")
            
            # Create transaction record for make_transaction
            if request.action == "make_transaction" and api_data.get("success"):
                amount = action_params.get("amount", 0)
                merchant = action_params.get("merchant", "Unknown Merchant")
                transaction_id = api_data.get("transaction_id", f"TXN{int(datetime.now().timestamp())}")
                
                new_transaction = Transaction(
                    user_id=current_user.user_id,
                    transaction_id=transaction_id,
                    amount=float(amount),
                    merchant=merchant,
                    category=action_params.get("category", "general"),
                    date=datetime.now(),
                    status="completed"
                )
                db.add(new_transaction)
                
                # Update available credit
                current_user.available_credit = max(0, current_user.available_credit - float(amount))
                
                db.commit()
                print(f"✅ Created transaction {transaction_id} for ₹{amount}")
            
            # Send WhatsApp notification for action execution
            try:
                action_details = {
                    **action_params,
                    **api_data,
                    "timestamp": datetime.now().isoformat()
                }
                await whatsapp_service.send_action_notification(
                    current_user.phone,
                    request.action,
                    action_details
                )
            except Exception as e:
                print(f"⚠️ Failed to send WhatsApp notification: {str(e)}")
            
            return {
                "success": True,
                "message": f"Action '{request.action}' executed successfully",
                "data": api_data
            }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Error executing action: {str(e)}"
            }
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

