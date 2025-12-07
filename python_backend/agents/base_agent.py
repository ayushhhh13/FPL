"""Base agent class for all category agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseAgent(ABC):
    """Base class for all category-specific agents."""
    
    def __init__(self, db_session):
        """
        Initialize agent with database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    @abstractmethod
    def handle_information_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Handle information retrieval queries.
        
        Args:
            query: User query
            user_id: User identifier
            
        Returns:
            Response dictionary with answer and data
        """
        pass
    
    @abstractmethod
    def handle_action_request(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Handle action execution requests.
        
        Args:
            query: User query
            user_id: User identifier
            
        Returns:
            Response dictionary with action details and consent requirement
        """
        pass
    
    def process(self, query: str, user_id: str, task_type: str) -> Dict[str, Any]:
        """
        Process query based on task type.
        
        Args:
            query: User query
            user_id: User identifier
            task_type: "information" or "action"
            
        Returns:
            Response dictionary
        """
        if task_type == "information":
            return self.handle_information_query(query, user_id)
        else:
            return self.handle_action_request(query, user_id)

