"""Agent for Transaction & EMI category."""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from database.models import Transaction
from datetime import datetime, timedelta


class TransactionAgent(BaseAgent):
    """Handle transaction and EMI related queries."""
    
    def handle_information_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle information queries about transactions."""
        query_lower = query.lower()
        
        if "emi" in query_lower:
            emi_transactions = self.db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.is_emi == True
            ).all()
            
            if not emi_transactions:
                return {
                    "answer": "You don't have any active EMI transactions.",
                    "data": [],
                    "requires_consent": False
                }
            
            emi_list = []
            for txn in emi_transactions:
                emi_list.append({
                    "transaction_id": txn.transaction_id,
                    "merchant": txn.merchant,
                    "total_amount": txn.amount,
                    "emi_tenure": txn.emi_tenure,
                    "emi_amount": txn.emi_amount,
                    "date": txn.date.isoformat()
                })
            
            return {
                "answer": f"You have {len(emi_list)} active EMI(s). Total EMI amount: ₹{sum(t['emi_amount'] for t in emi_list):,.2f}",
                "data": emi_list,
                "requires_consent": False
            }
        elif "recent" in query_lower or "last" in query_lower:
            limit = 5
            if "10" in query_lower:
                limit = 10
            
            transactions = self.db.query(Transaction).filter(
                Transaction.user_id == user_id
            ).order_by(Transaction.date.desc()).limit(limit).all()
            
            if not transactions:
                return {
                    "answer": "No recent transactions found.",
                    "data": [],
                    "requires_consent": False
                }
            
            txn_list = []
            for txn in transactions:
                txn_list.append({
                    "transaction_id": txn.transaction_id,
                    "merchant": txn.merchant,
                    "amount": txn.amount,
                    "category": txn.category,
                    "date": txn.date.isoformat(),
                    "status": txn.status
                })
            
            return {
                "answer": f"Here are your {len(txn_list)} recent transactions.",
                "data": txn_list,
                "requires_consent": False
            }
        else:
            # General transaction query
            transactions = self.db.query(Transaction).filter(
                Transaction.user_id == user_id
            ).order_by(Transaction.date.desc()).limit(10).all()
            
            total = sum(t.amount for t in transactions)
            
            return {
                "answer": f"You have {len(transactions)} transactions. Total amount: ₹{total:,.2f}",
                "data": [{
                    "transaction_id": t.transaction_id,
                    "merchant": t.merchant,
                    "amount": t.amount,
                    "date": t.date.isoformat()
                } for t in transactions],
                "requires_consent": False
            }
    
    def handle_action_request(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle action requests for transactions."""
        query_lower = query.lower()
        
        if "dispute" in query_lower or "chargeback" in query_lower:
            return {
                "answer": "I can help you dispute a transaction. Please provide the transaction ID.",
                "action": "dispute_transaction",
                "requires_consent": True,
                "consent_message": "Do you want to file a dispute for this transaction?"
            }
        elif "convert" in query_lower and "emi" in query_lower:
            return {
                "answer": "I can help you convert a transaction to EMI. Please provide the transaction ID.",
                "action": "convert_to_emi",
                "requires_consent": True,
                "consent_message": "Do you want to convert this transaction to EMI?"
            }
        else:
            return {
                "answer": "I can help you with transaction-related actions. What would you like to do?",
                "action": "transaction_action",
                "requires_consent": True,
                "consent_message": "Please specify the action you want to perform."
            }

