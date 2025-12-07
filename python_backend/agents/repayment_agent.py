"""Agent for Repayments category."""
from typing import Dict, Any
from .base_agent import BaseAgent
from database.models import Repayment, Bill
from datetime import datetime


class RepaymentAgent(BaseAgent):
    """Handle repayment related queries."""
    
    def handle_information_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle information queries about repayments."""
        query_lower = query.lower()
        
        if "history" in query_lower or "past" in query_lower:
            repayments = self.db.query(Repayment).filter(
                Repayment.user_id == user_id
            ).order_by(Repayment.payment_date.desc()).limit(10).all()
            
            if not repayments:
                return {
                    "answer": "No repayment history found.",
                    "data": [],
                    "requires_consent": False
                }
            
            repayment_list = []
            for payment in repayments:
                repayment_list.append({
                    "repayment_id": payment.repayment_id,
                    "amount": payment.amount,
                    "payment_method": payment.payment_method,
                    "status": payment.status,
                    "payment_date": payment.payment_date.isoformat()
                })
            
            return {
                "answer": f"You have {len(repayment_list)} repayment(s) in your history.",
                "data": repayment_list,
                "requires_consent": False
            }
        elif "method" in query_lower or "how" in query_lower:
            return {
                "answer": "You can make repayments using:\n"
                         "1. Bank Transfer\n"
                         "2. UPI\n"
                         "3. Debit Card\n"
                         "4. Net Banking",
                "data": {
                    "methods": ["bank_transfer", "upi", "debit_card", "net_banking"]
                },
                "requires_consent": False
            }
        else:
            # Get current bill for payment info
            bill = self.db.query(Bill).filter(
                Bill.user_id == user_id
            ).order_by(Bill.bill_date.desc()).first()
            
            if bill:
                return {
                    "answer": f"Your current bill amount is ₹{bill.total_amount:,.2f}. "
                             f"Minimum due: ₹{bill.minimum_due:,.2f}. "
                             f"Due date: {bill.due_date.strftime('%B %d, %Y')}",
                    "data": {
                        "total_amount": bill.total_amount,
                        "minimum_due": bill.minimum_due,
                        "due_date": bill.due_date.isoformat()
                    },
                    "requires_consent": False
                }
            else:
                return {
                    "answer": "I can help you with repayment information. What would you like to know?",
                    "data": None,
                    "requires_consent": False
                }
    
    def handle_action_request(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle action requests for repayments."""
        query_lower = query.lower()
        
        if "pay" in query_lower or "payment" in query_lower:
            bill = self.db.query(Bill).filter(
                Bill.user_id == user_id
            ).order_by(Bill.bill_date.desc()).first()
            
            if not bill:
                return {
                    "answer": "No pending bill found for payment.",
                    "action": None,
                    "requires_consent": False
                }
            
            amount = bill.minimum_due
            if "full" in query_lower or "total" in query_lower:
                amount = bill.total_amount
            
            return {
                "answer": f"I can help you make a payment of ₹{amount:,.2f}.",
                "action": "make_payment",
                "amount": amount,
                "requires_consent": True,
                "consent_message": f"Do you want to proceed with payment of ₹{amount:,.2f}?"
            }
        elif "schedule" in query_lower:
            return {
                "answer": "I can help you schedule a payment for a future date.",
                "action": "schedule_payment",
                "requires_consent": True,
                "consent_message": "Do you want to schedule a payment?"
            }
        else:
            return {
                "answer": "I can help you with repayment actions. What would you like to do?",
                "action": "repayment_action",
                "requires_consent": True,
                "consent_message": "Please specify the action you want to perform."
            }

