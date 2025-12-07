"""Agent for Collections category."""
from typing import Dict, Any
from .base_agent import BaseAgent
from database.models import Collection, Bill
from datetime import datetime


class CollectionsAgent(BaseAgent):
    """Handle collections related queries for overdue accounts."""
    
    def handle_information_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle information queries about collections."""
        collection = self.db.query(Collection).filter(
            Collection.user_id == user_id
        ).first()
        
        bill = self.db.query(Bill).filter(
            Bill.user_id == user_id,
            Bill.status == "overdue"
        ).order_by(Bill.due_date.desc()).first()
        
        query_lower = query.lower()
        
        if "overdue" in query_lower or "outstanding" in query_lower:
            if bill:
                days_overdue = (datetime.now() - bill.due_date).days
                return {
                    "answer": f"You have an overdue amount of ₹{bill.total_amount - bill.paid_amount:,.2f}. "
                             f"Days overdue: {days_overdue}. Please make payment to avoid further charges.",
                    "data": {
                        "overdue_amount": bill.total_amount - bill.paid_amount,
                        "days_overdue": days_overdue,
                        "bill_id": bill.bill_id,
                        "due_date": bill.due_date.isoformat()
                    },
                    "requires_consent": False
                }
            else:
                return {
                    "answer": "You don't have any overdue amounts.",
                    "data": None,
                    "requires_consent": False
                }
        elif "plan" in query_lower or "settlement" in query_lower:
            if collection and collection.payment_plan_offered:
                return {
                    "answer": "A payment plan has been offered for your account. Please contact customer support for details.",
                    "data": {
                        "payment_plan_offered": True,
                        "status": collection.status
                    },
                    "requires_consent": False
                }
            else:
                return {
                    "answer": "I can help you understand payment plan options. Would you like to know more?",
                    "data": None,
                    "requires_consent": False
                }
        else:
            if collection:
                return {
                    "answer": f"Collections status: {collection.status}. "
                             f"Overdue amount: ₹{collection.overdue_amount:,.2f}",
                    "data": {
                        "status": collection.status,
                        "overdue_amount": collection.overdue_amount,
                        "days_overdue": collection.days_overdue
                    },
                    "requires_consent": False
                }
            else:
                return {
                    "answer": "You don't have any active collections cases.",
                    "data": None,
                    "requires_consent": False
                }
    
    def handle_action_request(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle action requests for collections."""
        query_lower = query.lower()
        
        if "plan" in query_lower or "settlement" in query_lower:
            return {
                "answer": "I can help you set up a payment plan or settlement. This requires approval.",
                "action": "setup_payment_plan",
                "requires_consent": True,
                "consent_message": "Do you want to request a payment plan? A representative will contact you."
            }
        elif "pay" in query_lower:
            bill = self.db.query(Bill).filter(
                Bill.user_id == user_id,
                Bill.status == "overdue"
            ).first()
            
            if bill:
                return {
                    "answer": f"I can help you make a payment of ₹{bill.total_amount - bill.paid_amount:,.2f} to clear your overdue amount.",
                    "action": "pay_overdue",
                    "amount": bill.total_amount - bill.paid_amount,
                    "requires_consent": True,
                    "consent_message": f"Do you want to proceed with payment of ₹{bill.total_amount - bill.paid_amount:,.2f}?"
                }
            else:
                return {
                    "answer": "No overdue amount found.",
                    "action": None,
                    "requires_consent": False
                }
        else:
            return {
                "answer": "I can help you with collections-related actions. What would you like to do?",
                "action": "collections_action",
                "requires_consent": True,
                "consent_message": "Please specify the action you want to perform."
            }

