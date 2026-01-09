"""Main AI client for querying LLMs with financial data"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from .config import AIProvider, AIConfig, get_available_providers
from .providers import get_provider, BaseAIProvider
from .data_selector import DataSelector


class AIClient:
    """Main client for AI-powered financial analysis"""
    
    def __init__(self, db: Session, provider: Optional[AIProvider] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize AI client
        
        Args:
            db: Database session
            provider: AI provider to use (if None, will auto-detect)
            api_key: API key (if None, will auto-detect)
            model: Model to use (if None, uses provider default)
        """
        self.db = db
        self.data_selector = DataSelector(db)
        
        # Determine provider and API key
        if provider is None:
            available = get_available_providers()
            if not available:
                raise ValueError(
                    "No AI providers found. Please set API keys in .env or shell config files."
                )
            provider = available[0]  # Use first available
        
        if api_key is None:
            api_key = AIConfig.get_api_key(provider)
            if not api_key:
                raise ValueError(
                    f"No API key found for {provider.value}. "
                    f"Please set it in .env or shell config files."
                )
        
        self.provider = provider
        self.ai_provider: BaseAIProvider = get_provider(provider, api_key, model=model)
    
    def query(self, user_query: str, include_full_data: bool = False) -> Dict[str, Any]:
        """
        Query AI with user's question and relevant financial data
        
        Args:
            user_query: User's question
            include_full_data: If True, include full database export (use with caution)
            
        Returns:
            Dictionary with AI response and metadata
        """
        # Select relevant data based on query intent
        if include_full_data:
            # Use full export for comprehensive analysis
            from ..api.export import export_accounts, export_holdings, export_transactions, export_summary_statistics
            context_data = {
                "accounts": export_accounts(self.db),
                "holdings": export_holdings(self.db),
                "transactions": export_transactions(self.db),
                "summary": export_summary_statistics(self.db),
            }
        else:
            # Use intelligent data selection
            context_data = self.data_selector.select_data(user_query)
        
        # Query AI
        try:
            response = self.ai_provider.query(user_query, context=context_data)
            
            return {
                "query": user_query,
                "provider": self.provider.value,
                "response": response,
                "data_included": {
                    "keys": list(context_data.keys()),
                    "transaction_count": len(context_data.get("transactions", [])) if isinstance(context_data.get("transactions"), list) else 0,
                },
            }
        except Exception as e:
            return {
                "query": user_query,
                "provider": self.provider.value,
                "error": str(e),
                "data_included": {
                    "keys": list(context_data.keys()),
                },
            }
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available providers with API keys"""
        return get_available_providers()
    
    @classmethod
    def list_providers_with_keys(cls) -> Dict[AIProvider, list]:
        """List all providers with their detected API key sources"""
        return AIConfig.detect_api_keys()
