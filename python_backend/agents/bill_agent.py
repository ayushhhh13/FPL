"""Agent for Bill & Statement category."""
from typing import Dict, Any
from .base_agent import BaseAgent
from database.models import Bill
from datetime import datetime


class BillAgent(BaseAgent):
    """Handle bill and statement related queries."""
    
    def handle_information_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle information queries about bills."""
        bill = self.db.query(Bill).filter(
            Bill.user_id == user_id
        ).order_by(Bill.bill_date.desc()).first()
        
        if not bill:
            return {
                "answer": "I couldn't find any bill information for your account.",
                "data": None,
                "requires_consent": False
            }
        
        query_lower = query.lower()
        
        if "due date" in query_lower or "due" in query_lower:
            days_remaining = (bill.due_date - datetime.now()).days
            return {
                "answer": f"Your bill due date is {bill.due_date.strftime('%B %d, %Y')}. "
                         f"You have {days_remaining} days remaining. Total amount: ₹{bill.total_amount:,.2f}",
                "data": {
                    "due_date": bill.due_date.isoformat(),
                    "total_amount": bill.total_amount,
                    "minimum_due": bill.minimum_due,
                    "days_remaining": days_remaining
                },
                "requires_consent": False
            }
        elif "amount" in query_lower or "total" in query_lower:
            return {
                "answer": f"Your current bill amount is ₹{bill.total_amount:,.2f}. "
                         f"Minimum due: ₹{bill.minimum_due:,.2f}",
                "data": {
                    "total_amount": bill.total_amount,
                    "minimum_due": bill.minimum_due,
                    "paid_amount": bill.paid_amount,
                    "outstanding": bill.total_amount - bill.paid_amount
                },
                "requires_consent": False
            }
        elif "statement" in query_lower or "download" in query_lower:
            return {
                "answer": f"I can help you download your statement. Bill ID: {bill.bill_id}, "
                         f"Amount: ₹{bill.total_amount:,.2f}",
                "data": {
                    "bill_id": bill.bill_id,
                    "bill_date": bill.bill_date.isoformat(),
                    "statement_pdf_url": bill.statement_pdf_url
                },
                "requires_consent": False
            }
        else:
            return {
                "answer": f"Your current bill: ₹{bill.total_amount:,.2f}, "
                         f"Due date: {bill.due_date.strftime('%B %d, %Y')}, "
                         f"Status: {bill.status}",
                "data": {
                    "bill_id": bill.bill_id,
                    "total_amount": bill.total_amount,
                    "due_date": bill.due_date.isoformat(),
                    "status": bill.status
                },
                "requires_consent": False
            }
    
    def handle_action_request(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle action requests for bills."""
        query_lower = query.lower()
        
        if "download" in query_lower or "statement" in query_lower:
            return {
                "answer": "I can help you download your statement PDF.",
                "action": "download_statement",
                "requires_consent": True,
                "consent_message": "Do you want to download your statement now?"
            }
        elif "email" in query_lower and "statement" in query_lower:
            return {
                "answer": "I can email your statement to your registered email address.",
                "action": "email_statement",
                "requires_consent": True,
                "consent_message": "Do you want to email the statement to your registered email?"
            }
        else:
            return {
                "answer": "I can help you with bill-related actions. What would you like to do?",
                "action": "bill_action",
                "requires_consent": True,
                "consent_message": "Please specify the action you want to perform."
            }

