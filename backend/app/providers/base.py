"""Abstract base classes for financial data providers"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import date


class ProviderType(Enum):
    """Supported financial data providers"""
    PLAID = "plaid"
    TELLER = "teller"
    # Future providers can be added here


class BaseProviderClient(ABC):
    """Abstract base class for financial data provider clients"""
    
    @abstractmethod
    def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Get all accounts for an access token
        
        Args:
            access_token: Provider access token
            
        Returns:
            List of account dictionaries with standardized format:
            {
                "id": str,
                "item_id": str,
                "name": str,
                "official_name": Optional[str],
                "type": str,
                "subtype": Optional[str],
                "mask": Optional[str],
                "balances": {
                    "available": Optional[float],
                    "current": Optional[float],
                    "limit": Optional[float],
                },
                "institution_id": Optional[str],
                "raw_data": Optional[str],  # JSON string of provider-specific data
            }
        """
        pass
    
    @abstractmethod
    def get_investment_holdings(self, access_token: str) -> Dict[str, Any]:
        """
        Get investment holdings for an access token
        
        Args:
            access_token: Provider access token
            
        Returns:
            Dictionary with standardized format:
            {
                "accounts": List[Dict],
                "holdings": Dict[account_id, List[Dict]],  # Holdings by account
                "securities": List[Dict],
            }
        """
        pass
    
    @abstractmethod
    def get_investment_transactions(
        self,
        access_token: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Get investment transactions for a date range
        
        Args:
            access_token: Provider access token
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of transaction dictionaries with standardized format
        """
        pass
    
    @abstractmethod
    def get_transactions(
        self,
        access_token: str,
        start_date: str,
        end_date: str,
        account_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get regular banking transactions (checking, savings, credit cards)
        
        Args:
            access_token: Provider access token
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            account_ids: Optional list of account IDs to filter by
            
        Returns:
            List of transaction dictionaries with standardized format
        """
        pass
    
    @abstractmethod
    def create_link_token(self, redirect_uri: Optional[str] = None) -> str:
        """
        Create a link token for provider's connection flow
        
        Args:
            redirect_uri: Optional URI to redirect to after connection completes
            
        Returns:
            Link token string
        """
        pass
    
    @abstractmethod
    def exchange_public_token(self, public_token: str) -> tuple[str, str]:
        """
        Exchange a public token for an access token
        
        Args:
            public_token: Public token from provider's connection flow
            
        Returns:
            Tuple of (access_token, item_id)
        """
        pass


class BaseProviderSync(ABC):
    """Abstract base class for syncing provider data to database"""
    
    def __init__(self, provider_client: BaseProviderClient):
        """
        Initialize sync handler
        
        Args:
            provider_client: Provider client instance
        """
        self.provider_client = provider_client
    
    @abstractmethod
    def sync_accounts(
        self,
        db,
        access_token: str,
        item_id: str
    ) -> List:
        """
        Sync accounts from provider to database
        
        Args:
            db: Database session
            access_token: Provider access token
            item_id: Provider item ID
            
        Returns:
            List of synced Account objects
        """
        pass
    
    @abstractmethod
    def sync_holdings(
        self,
        db,
        access_token: str,
        as_of_date: Optional[date] = None
    ) -> List:
        """
        Sync investment holdings from provider to database
        
        Args:
            db: Database session
            access_token: Provider access token
            as_of_date: Date for the holdings snapshot (defaults to today)
            
        Returns:
            List of synced Holding objects
        """
        pass
    
    @abstractmethod
    def sync_transactions(
        self,
        db,
        access_token: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sync_investment: bool = True,
        sync_banking: bool = True
    ) -> List:
        """
        Sync transactions from provider to database
        
        Args:
            db: Database session
            access_token: Provider access token
            start_date: Start date for transactions
            end_date: End date for transactions
            sync_investment: Whether to sync investment transactions
            sync_banking: Whether to sync regular banking transactions
            
        Returns:
            List of synced Transaction objects
        """
        pass
    
    @abstractmethod
    def sync_all(
        self,
        db,
        access_token: str,
        item_id: str,
        sync_holdings: bool = True,
        sync_transactions: bool = True
    ) -> dict:
        """
        Sync all data from provider (accounts, holdings, transactions)
        
        Args:
            db: Database session
            access_token: Provider access token
            item_id: Provider item ID
            sync_holdings: Whether to sync holdings
            sync_transactions: Whether to sync transactions
            
        Returns:
            Dictionary with sync results:
            {
                "accounts": int,
                "holdings": int,
                "transactions": int,
            }
        """
        pass
