"""Teller provider client implementation"""

from typing import Optional, Dict, Any, List
import json
import os

from .base import BaseProviderClient
from ..config import config


class TellerClient(BaseProviderClient):
    """Teller implementation of BaseProviderClient"""
    
    def __init__(
        self,
        application_id: Optional[str] = None,
        certificate_path: Optional[str] = None,
        private_key_path: Optional[str] = None,
        environment: Optional[str] = None
    ):
        """
        Initialize Teller client
        
        Args:
            application_id: Teller application ID (defaults to config)
            certificate_path: Path to Teller certificate.pem (defaults to config)
            private_key_path: Path to Teller private_key.pem (defaults to config)
            environment: Teller environment (sandbox or production, defaults to config)
        """
        try:
            import teller
        except ImportError:
            raise ImportError(
                "Teller SDK not installed. Install with: pip install teller-python"
            )
        
        self.application_id = application_id or config.TELLER_APPLICATION_ID
        self.certificate_path = certificate_path or config.TELLER_CERTIFICATE_PATH
        self.private_key_path = private_key_path or config.TELLER_PRIVATE_KEY_PATH
        self.environment = environment or getattr(config, 'TELLER_ENV', 'sandbox')
        
        if not self.application_id:
            raise ValueError("Teller application_id must be provided")
        if not self.certificate_path or not os.path.exists(self.certificate_path):
            raise ValueError(f"Teller certificate not found at: {self.certificate_path}")
        if not self.private_key_path or not os.path.exists(self.private_key_path):
            raise ValueError(f"Teller private key not found at: {self.private_key_path}")
        
        # Initialize Teller client
        self.client = teller.Client(
            application_id=self.application_id,
            certificate_path=self.certificate_path,
            private_key_path=self.private_key_path,
            environment=self.environment
        )
    
    def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """Get all accounts for an access token"""
        try:
            accounts = self.client.accounts.list(access_token=access_token)
            
            # Convert to standardized format
            standardized_accounts = []
            for acc in accounts:
                # Get balance for each account
                try:
                    balance_data = self.client.accounts.balances(acc['id'], access_token=access_token)
                except Exception:
                    balance_data = {}
                
                standardized_accounts.append({
                    "id": acc.get("id"),
                    "item_id": acc.get("enrollment_id"),  # Teller uses enrollment_id
                    "name": acc.get("name", ""),
                    "official_name": acc.get("name", ""),
                    "type": self._map_teller_account_type(acc.get("type", "")),
                    "subtype": acc.get("subtype"),
                    "mask": acc.get("account_number", {}).get("last_4") if isinstance(acc.get("account_number"), dict) else None,
                    "balances": {
                        "available": float(balance_data.get("available", 0)) if balance_data.get("available") else None,
                        "current": float(balance_data.get("ledger", 0)) if balance_data.get("ledger") else None,
                        "limit": float(acc.get("credit_limit", 0)) if acc.get("credit_limit") else None,
                    },
                    "institution_id": acc.get("institution", {}).get("id") if isinstance(acc.get("institution"), dict) else None,
                    "raw_data": json.dumps(acc),
                })
            
            return standardized_accounts
        except Exception as e:
            raise Exception(f"Failed to get accounts: {str(e)}")
    
    def get_investment_holdings(self, access_token: str) -> Dict[str, Any]:
        """Get investment holdings for an access token"""
        # Teller doesn't support investment holdings in the same way as Plaid
        # Return empty structure for now
        return {
            "accounts": [],
            "holdings": {},
            "securities": [],
        }
    
    def get_investment_transactions(
        self,
        access_token: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get investment transactions for a date range"""
        # Teller doesn't support investment transactions separately
        # Return empty list for now
        return []
    
    def get_transactions(
        self,
        access_token: str,
        start_date: str,
        end_date: str,
        account_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get regular banking transactions"""
        try:
            all_transactions = []
            
            # Get accounts if not provided
            if account_ids is None:
                accounts = self.client.accounts.list(access_token=access_token)
                account_ids = [acc['id'] for acc in accounts]
            
            # Get transactions for each account
            for account_id in account_ids:
                try:
                    transactions = self.client.transactions.list(
                        account_id=account_id,
                        access_token=access_token,
                        from_date=start_date,
                        to_date=end_date
                    )
                    
                    for txn in transactions:
                        standardized_txn = self._standardize_transaction(txn, account_id)
                        all_transactions.append(standardized_txn)
                except Exception as e:
                    # Skip accounts that fail
                    continue
            
            return all_transactions
        except Exception as e:
            raise Exception(f"Failed to get transactions: {str(e)}")
    
    def create_link_token(self, redirect_uri: Optional[str] = None) -> str:
        """Create a link token for Teller Connect"""
        # Teller uses Connect URLs, not link tokens
        # Return a Connect URL instead
        try:
            connect_url = self.client.connect.create_url(
                redirect_uri=redirect_uri or "http://localhost:8080/success"
            )
            return connect_url
        except Exception as e:
            raise Exception(f"Failed to create Teller Connect URL: {str(e)}")
    
    def exchange_public_token(self, authorization_code: str) -> tuple[str, str]:
        """Exchange authorization code for access token"""
        try:
            # Teller uses authorization code, not public token
            access_token = self.client.connect.exchange_code_for_token(authorization_code)
            # Teller doesn't have item_id, use enrollment_id or account_id
            # Get first account to get enrollment_id
            accounts = self.client.accounts.list(access_token=access_token)
            enrollment_id = accounts[0].get("enrollment_id") if accounts else access_token
            return access_token, enrollment_id
        except Exception as e:
            raise Exception(f"Failed to exchange authorization code: {str(e)}")
    
    def _map_teller_account_type(self, teller_type: str) -> str:
        """Map Teller account type to standardized type"""
        type_map = {
            "depository": "depository",
            "credit": "credit",
            "loan": "loan",
            "investment": "investment",
            "other": "other",
        }
        return type_map.get(teller_type.lower(), "other")
    
    def _standardize_transaction(self, txn: dict, account_id: str) -> dict:
        """Convert Teller transaction to standardized format"""
        return {
            "id": txn.get("id"),
            "account_id": account_id,
            "date": txn.get("date"),
            "transaction_datetime": txn.get("timestamp"),
            "name": txn.get("description", ""),
            "amount": float(txn.get("amount", {}).get("value", 0)) if isinstance(txn.get("amount"), dict) else float(txn.get("amount", 0)),
            "type": "expense" if (txn.get("amount", {}).get("value", 0) if isinstance(txn.get("amount"), dict) else txn.get("amount", 0)) < 0 else "income",
            "subtype": txn.get("type"),
            "category": txn.get("category"),
            "primary_category": txn.get("category"),
            "detailed_category": txn.get("category"),
            "merchant_name": txn.get("merchant", {}).get("name") if isinstance(txn.get("merchant"), dict) else None,
            "location_city": None,
            "location_region": None,
            "location_country": None,
            "location_address": None,
            "location_postal_code": None,
            "iso_currency_code": txn.get("amount", {}).get("currency") if isinstance(txn.get("amount"), dict) else "USD",
            "unofficial_currency_code": None,
            "is_pending": txn.get("status") == "pending",
            "plaid_data": json.dumps(txn),  # Store Teller data in plaid_data field for now
        }
