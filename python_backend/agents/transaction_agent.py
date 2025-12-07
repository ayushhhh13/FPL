"""Agent for Transaction & EMI category."""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from database.models import Transaction, User
from datetime import datetime, timedelta
import re


class TransactionAgent(BaseAgent):
    """Handle transaction and EMI related queries."""
    
    def _extract_amount(self, query: str) -> float:
        """Extract amount from query text."""
        # Patterns to match amounts like "1000", "1000 rs", "1000 rupees", "₹1000", etc.
        patterns = [
            r'₹\s*([\d,]+\.?\d*)',  # ₹1000 or ₹1,000
            r'([\d,]+\.?\d*)\s*(?:rs|rupees?|rupee)',  # 1000 rs, 1000 rupees
            r'(?:for|of|amount|pay|transaction|purchase|buy)\s+(?:₹)?\s*([\d,]+\.?\d*)',  # for 1000, of ₹1000
            r'([\d,]+\.?\d*)',  # Just numbers (fallback)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    if amount > 0:
                        return amount
                except ValueError:
                    continue
        
        return 0.0
    
    def _extract_merchant(self, query: str) -> str:
        """Extract merchant name from query if mentioned."""
        # Common merchant patterns
        merchants = ["amazon", "flipkart", "swiggy", "zomato", "uber", "ola", "restaurant", "store", "shop"]
        query_lower = query.lower()
        
        for merchant in merchants:
            if merchant in query_lower:
                return merchant.capitalize()
        
        return "Unknown Merchant"
    
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
        
        # Check if card is blocked before allowing transactions
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if user and user.card_status == "blocked":
            return {
                "answer": "❌ Your card is currently blocked. Please unblock your card first to make transactions.",
                "action": None,
                "requires_consent": False
            }
        
        # Check for make transaction / purchase requests
        if any(keyword in query_lower for keyword in ["make transaction", "purchase", "buy", "pay", "transaction for", "spend"]):
            amount = self._extract_amount(query)
            merchant = self._extract_merchant(query)
            
            if amount <= 0:
                return {
                    "answer": "I can help you make a transaction. Please specify the amount (e.g., 'make a transaction for 1000 rupees').",
                    "action": None,
                    "requires_consent": False
                }
            
            # Check available credit
            if user and amount > user.available_credit:
                return {
                    "answer": f"❌ Transaction failed: Insufficient credit. Available: ₹{user.available_credit:,.2f}, Required: ₹{amount:,.2f}",
                    "action": None,
                    "requires_consent": False
                }
            
            return {
                "answer": f"I can help you make a transaction of ₹{amount:,.2f} at {merchant}.",
                "action": "make_transaction",
                "action_params": {
                    "amount": amount,
                    "merchant": merchant,
                    "category": "general"
                },
                "requires_consent": True,
                "consent_message": f"Do you want to proceed with transaction of ₹{amount:,.2f} at {merchant}?"
            }
        elif "dispute" in query_lower or "chargeback" in query_lower:
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

