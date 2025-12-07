"""Query classifier using LLM."""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Query categories
CATEGORIES = {
    "account": "Account & Onboarding",
    "delivery": "Card Delivery",
    "transaction": "Transaction & EMI",
    "bill": "Bill & Statement",
    "repayment": "Repayments",
    "collections": "Collections"
}

# Task types
TASK_TYPES = {
    "information": "Information Retrieval",
    "action": "Action Execution"
}


class QueryClassifier:
    """Classify user queries into categories and task types."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
            print("⚠️  Warning: OPENAI_API_KEY not set. Classification will use fallback method.")
            self.client = None
            self.use_fallback = True
        else:
            self.client = OpenAI(api_key=api_key)
            self.use_fallback = False
    
    def classify(self, query: str) -> dict:
        """
        Classify query into category and task type.
        
        Args:
            query: User query text
            
        Returns:
            Dictionary with category, task_type, and confidence
        """
        prompt = f"""Classify the following credit card customer query into one category and task type.

Categories:
- account: Account & Onboarding (account details, card activation, KYC, profile updates)
- delivery: Card Delivery (tracking, delivery status, address updates)
- transaction: Transaction & EMI (transaction history, EMI details, dispute transactions)
- bill: Bill & Statement (bill amount, due date, statement download, bill details)
- repayment: Repayments (payment methods, payment history, schedule payment)
- collections: Collections (overdue amounts, payment plans, settlement)

Task Types:
- information: Information Retrieval (read-only queries, no actions)
- action: Action Execution (requires user consent, modifies data or initiates transactions)

Query: "{query}"

Respond ONLY in JSON format:
{{
    "category": "one of: account, delivery, transaction, bill, repayment, collections",
    "task_type": "information or action",
    "reasoning": "brief explanation"
}}"""

        # Use fallback classification if OpenAI is not available
        if self.use_fallback or not self.client:
            return self._fallback_classify(query)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a query classifier. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150  # Low token usage as requested
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            # Validate category
            if result["category"] not in CATEGORIES:
                result["category"] = "account"  # Default fallback
            
            # Validate task type
            if result["task_type"] not in TASK_TYPES:
                result["task_type"] = "information"  # Default fallback
            
            return {
                "category": result["category"],
                "task_type": result["task_type"],
                "category_name": CATEGORIES[result["category"]],
                "task_type_name": TASK_TYPES[result["task_type"]],
                "reasoning": result.get("reasoning", "")
            }
        except Exception as e:
            print(f"Error in classification: {e}")
            return self._fallback_classify(query)
    
    def _fallback_classify(self, query: str) -> dict:
        """Fallback classification using keyword matching."""
        query_lower = query.lower()
        
        # Category detection
        if any(word in query_lower for word in ["delivery", "track", "ship", "card delivery"]):
            category = "delivery"
        elif any(word in query_lower for word in ["transaction", "emi", "purchase", "spent"]):
            category = "transaction"
        elif any(word in query_lower for word in ["bill", "statement", "due date", "invoice"]):
            category = "bill"
        elif any(word in query_lower for word in ["payment", "repay", "pay", "settle"]):
            category = "repayment"
        elif any(word in query_lower for word in ["overdue", "collection", "outstanding"]):
            category = "collections"
        else:
            category = "account"
        
        # Task type detection - check for action keywords
        # First check for specific action verbs
        if any(word in query_lower for word in ["block", "unblock", "activate", "deactivate"]):
            task_type = "action"
        elif any(word in query_lower for word in ["update", "change", "make", "do", "want to", "help me", "i want", "i need", "please"]):
            task_type = "action"
        else:
            task_type = "information"
        
        return {
            "category": category,
            "task_type": task_type,
            "category_name": CATEGORIES[category],
            "task_type_name": TASK_TYPES[task_type],
            "reasoning": "Fallback keyword-based classification"
        }

