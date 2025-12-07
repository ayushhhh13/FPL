"""Agent for Account & Onboarding category."""
from typing import Dict, Any
from .base_agent import BaseAgent
from database.models import User


class AccountAgent(BaseAgent):
    """Handle account and onboarding related queries."""
    
    def handle_information_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle information queries about account."""
        user = self.db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            return {
                "answer": "I couldn't find your account. Please contact customer support.",
                "data": None,
                "requires_consent": False
            }
        
        # Simple keyword-based response generation
        query_lower = query.lower()
        
        if "balance" in query_lower or "available" in query_lower:
            return {
                "answer": f"Your available credit is ₹{user.available_credit:,.2f} out of ₹{user.credit_limit:,.2f} credit limit.",
                "data": {
                    "available_credit": user.available_credit,
                    "credit_limit": user.credit_limit
                },
                "requires_consent": False
            }
        elif "status" in query_lower or "active" in query_lower:
            return {
                "answer": f"Your card status is {user.card_status}. Card number: {user.card_number}",
                "data": {
                    "card_status": user.card_status,
                    "card_number": user.card_number
                },
                "requires_consent": False
            }
        elif "profile" in query_lower or "details" in query_lower:
            return {
                "answer": f"Account Details:\nName: {user.name}\nEmail: {user.email}\nPhone: {user.phone}\nCard: {user.card_number}",
                "data": {
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                    "card_number": user.card_number
                },
                "requires_consent": False
            }
        else:
            return {
                "answer": f"Your account is active. Available credit: ₹{user.available_credit:,.2f}",
                "data": {
                    "user_id": user.user_id,
                    "card_status": user.card_status
                },
                "requires_consent": False
            }
    
    def handle_action_request(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle action requests for account updates."""
        query_lower = query.lower()
        
        # Check for unblock first (since "unblock" contains "block")
        if "unblock" in query_lower and ("card" in query_lower or "credit" in query_lower):
            return {
                "answer": "I can help you unblock your credit card. This will restore normal card functionality.",
                "action": "unblock_card",
                "requires_consent": True,
                "consent_message": "Do you want to unblock your credit card now?"
            }
        elif "block" in query_lower and ("card" in query_lower or "credit" in query_lower):
            return {
                "answer": "I can help you block your credit card. This will prevent all transactions until you unblock it.",
                "action": "block_card",
                "requires_consent": True,
                "consent_message": "⚠️ Are you sure you want to block your credit card? This will prevent all transactions immediately."
            }
        elif "update" in query_lower or "change" in query_lower:
            if "email" in query_lower:
                return {
                    "answer": "I can help you update your email address. This will require verification.",
                    "action": "update_email",
                    "requires_consent": True,
                    "consent_message": "Do you want to proceed with updating your email address?"
                }
            elif "phone" in query_lower:
                return {
                    "answer": "I can help you update your phone number. This will require OTP verification.",
                    "action": "update_phone",
                    "requires_consent": True,
                    "consent_message": "Do you want to proceed with updating your phone number?"
                }
            else:
                return {
                    "answer": "I can help you update your profile information. What would you like to update?",
                    "action": "update_profile",
                    "requires_consent": True,
                    "consent_message": "Please specify what information you want to update."
                }
        elif "activate" in query_lower:
            return {
                "answer": "I can help you activate your credit card.",
                "action": "activate_card",
                "requires_consent": True,
                "consent_message": "Do you want to activate your credit card now?"
            }
        else:
            return {
                "answer": "I can help you with account-related actions. What would you like to do?",
                "action": "account_action",
                "requires_consent": True,
                "consent_message": "Please specify the action you want to perform."
            }

