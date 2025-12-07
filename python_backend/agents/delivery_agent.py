"""Agent for Card Delivery category."""
from typing import Dict, Any
from .base_agent import BaseAgent
from database.models import CardDelivery


class DeliveryAgent(BaseAgent):
    """Handle card delivery related queries."""
    
    def handle_information_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle information queries about card delivery."""
        delivery = self.db.query(CardDelivery).filter(
            CardDelivery.user_id == user_id
        ).order_by(CardDelivery.created_at.desc()).first()
        
        if not delivery:
            return {
                "answer": "I couldn't find any delivery information for your account.",
                "data": None,
                "requires_consent": False
            }
        
        query_lower = query.lower()
        
        if "track" in query_lower or "status" in query_lower:
            status_messages = {
                "processing": "Your card is being processed and will be shipped soon.",
                "shipped": "Your card has been shipped.",
                "in_transit": "Your card is in transit to your address.",
                "delivered": "Your card has been delivered."
            }
            
            message = status_messages.get(delivery.status, f"Status: {delivery.status}")
            
            return {
                "answer": f"{message} Tracking number: {delivery.tracking_number}. "
                         f"Delivery address: {delivery.address}",
                "data": {
                    "tracking_number": delivery.tracking_number,
                    "status": delivery.status,
                    "address": delivery.address,
                    "estimated_delivery": delivery.estimated_delivery.isoformat() if delivery.estimated_delivery else None,
                    "actual_delivery": delivery.actual_delivery.isoformat() if delivery.actual_delivery else None
                },
                "requires_consent": False
            }
        else:
            return {
                "answer": f"Your card delivery status: {delivery.status}. Tracking: {delivery.tracking_number}",
                "data": {
                    "status": delivery.status,
                    "tracking_number": delivery.tracking_number
                },
                "requires_consent": False
            }
    
    def handle_action_request(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle action requests for delivery updates."""
        query_lower = query.lower()
        
        if "update" in query_lower and "address" in query_lower:
            return {
                "answer": "I can help you update your delivery address. This may delay your delivery.",
                "action": "update_delivery_address",
                "requires_consent": True,
                "consent_message": "Do you want to update your delivery address?"
            }
        elif "reschedule" in query_lower:
            return {
                "answer": "I can help you reschedule your card delivery.",
                "action": "reschedule_delivery",
                "requires_consent": True,
                "consent_message": "Do you want to reschedule your card delivery?"
            }
        else:
            return {
                "answer": "I can help you with delivery-related actions. What would you like to do?",
                "action": "delivery_action",
                "requires_consent": True,
                "consent_message": "Please specify the action you want to perform."
            }

