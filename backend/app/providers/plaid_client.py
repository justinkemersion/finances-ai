"""Plaid provider client implementation"""

from plaid.api import plaid_api
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid import Environment
from typing import Optional, Dict, Any, List
import json

from .base import BaseProviderClient
from ..config import config


class PlaidClient(BaseProviderClient):
    """Plaid implementation of BaseProviderClient"""
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        secret: Optional[str] = None,
        environment: Optional[str] = None
    ):
        """
        Initialize Plaid client
        
        Args:
            client_id: Plaid client ID (defaults to config)
            secret: Plaid secret (defaults to config)
            environment: Plaid environment (defaults to config)
        """
        self.client_id = client_id or config.PLAID_CLIENT_ID
        self.secret = secret or config.PLAID_SECRET
        self.environment = environment or config.PLAID_ENV
        
        if not self.client_id or not self.secret:
            raise ValueError("Plaid client_id and secret must be provided")
        
        # Map environment string to Plaid host
        host_map = {
            "sandbox": Environment.Sandbox,
            "development": Environment.Production,  # Development uses Production endpoint
            "production": Environment.Production,
        }
        
        plaid_host = host_map.get(self.environment.lower())
        if not plaid_host:
            raise ValueError(f"Invalid Plaid environment: {self.environment}")
        
        # Configure Plaid
        plaid_config = Configuration(
            host=plaid_host,
            api_key={
                "clientId": self.client_id,
                "secret": self.secret,
            }
        )
        
        api_client = ApiClient(plaid_config)
        self.client = plaid_api.PlaidApi(api_client)
    
    def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """Get all accounts for an access token"""
        try:
            from plaid.model.accounts_get_request import AccountsGetRequest
            
            request = AccountsGetRequest(access_token=access_token)
            response = self.client.accounts_get(request)
            return [
                {
                    "id": acc.account_id,
                    "item_id": response.item.item_id,
                    "name": acc.name,
                    "official_name": acc.official_name,
                    "type": acc.type.value if hasattr(acc.type, "value") else str(acc.type),
                    "subtype": acc.subtype.value if hasattr(acc.subtype, "value") else str(acc.subtype) if acc.subtype else None,
                    "mask": acc.mask,
                    "balances": {
                        "available": float(acc.balances.available) if acc.balances.available else None,
                        "current": float(acc.balances.current) if acc.balances.current else None,
                        "limit": float(acc.balances.limit) if acc.balances.limit else None,
                    },
                    "institution_id": response.item.institution_id,
                    "raw_data": json.dumps(acc.to_dict()) if hasattr(acc, "to_dict") else None,
                }
                for acc in response.accounts
            ]
        except Exception as e:
            raise Exception(f"Failed to get accounts: {str(e)}")
    
    def get_investment_holdings(self, access_token: str) -> Dict[str, Any]:
        """Get investment holdings for an access token"""
        try:
            from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
            
            request = InvestmentsHoldingsGetRequest(access_token=access_token)
            response = self.client.investments_holdings_get(request)
            
            # Convert to standardized format
            securities_map = {
                sec.security_id: {
                    "id": sec.security_id,
                    "name": sec.name,
                    "ticker": sec.ticker_symbol,
                    "cusip": sec.cusip,
                    "isin": sec.isin,
                    "sedol": sec.sedol,
                    "type": sec.type.value if hasattr(sec.type, "value") else str(sec.type),
                }
                for sec in response.securities
            }
            
            holdings_by_account = {}
            for holding in response.holdings:
                account_id = holding.account_id
                if account_id not in holdings_by_account:
                    holdings_by_account[account_id] = []
                
                security = securities_map.get(holding.security_id, {})
                holdings_by_account[account_id].append({
                    "account_id": account_id,
                    "security_id": holding.security_id,
                    "quantity": float(holding.quantity) if holding.quantity else 0.0,
                    "price": float(holding.institution_price) if hasattr(holding, 'institution_price') and holding.institution_price else None,
                    "value": float(holding.institution_value) if holding.institution_value else None,
                    "cost_basis": float(holding.cost_basis) if holding.cost_basis else None,
                    "security": security,
                })
            
            return {
                "accounts": [
                    {
                        "id": acc.account_id,
                        "name": acc.name,
                        "type": acc.type.value if hasattr(acc.type, "value") else str(acc.type),
                    }
                    for acc in response.accounts
                ],
                "holdings": holdings_by_account,
                "securities": list(securities_map.values()),
            }
        except Exception as e:
            raise Exception(f"Failed to get investment holdings: {str(e)}")
    
    def get_investment_transactions(
        self,
        access_token: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get investment transactions for a date range"""
        try:
            from datetime import datetime
            from plaid.model.investments_transactions_get_request import InvestmentsTransactionsGetRequest
            
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            request = InvestmentsTransactionsGetRequest(
                access_token=access_token,
                start_date=start,
                end_date=end
            )
            response = self.client.investments_transactions_get(request)
            
            transactions = []
            for txn in response.investment_transactions:
                txn_dict = txn.to_dict() if hasattr(txn, 'to_dict') else {}
                
                import json
                from datetime import date, datetime
                def json_serial(obj):
                    if isinstance(obj, (datetime, date)):
                        return obj.isoformat()
                    raise TypeError(f"Type {type(obj)} not serializable")
                
                txn_dict_str = json.dumps(txn_dict, default=json_serial)
                txn_dict = json.loads(txn_dict_str)
                
                transaction_datetime = None
                if hasattr(txn, 'transaction_datetime') and txn.transaction_datetime:
                    transaction_datetime = txn.transaction_datetime.isoformat() if hasattr(txn.transaction_datetime, 'isoformat') else str(txn.transaction_datetime)
                
                transactions.append({
                    "id": txn.investment_transaction_id,
                    "account_id": txn.account_id,
                    "date": txn.date.isoformat() if hasattr(txn.date, "isoformat") else str(txn.date),
                    "transaction_datetime": transaction_datetime,
                    "name": txn.name,
                    "amount": float(txn.amount),
                    "type": txn.type.value if hasattr(txn.type, "value") else str(txn.type),
                    "subtype": txn.subtype.value if hasattr(txn.subtype, "value") else str(txn.subtype) if txn.subtype else None,
                    "quantity": float(txn.quantity) if txn.quantity else None,
                    "price": float(txn.price) if txn.price else None,
                    "fees": float(txn.fees) if hasattr(txn, 'fees') and txn.fees else None,
                    "security_id": txn.security_id,
                    "iso_currency_code": txn.iso_currency_code if hasattr(txn, 'iso_currency_code') else None,
                    "unofficial_currency_code": txn.unofficial_currency_code if hasattr(txn, 'unofficial_currency_code') else None,
                    "cancel_transaction_id": txn.cancel_transaction_id if hasattr(txn, 'cancel_transaction_id') and txn.cancel_transaction_id else None,
                    "is_pending": False,
                    "plaid_data": txn_dict,
                })
            
            return transactions
        except Exception as e:
            raise Exception(f"Failed to get investment transactions: {str(e)}")
    
    def get_transactions(
        self,
        access_token: str,
        start_date: str,
        end_date: str,
        account_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get regular banking transactions"""
        try:
            from datetime import datetime
            from plaid.model.transactions_get_request import TransactionsGetRequest
            from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
            
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            options = TransactionsGetRequestOptions()
            if account_ids:
                options.account_ids = account_ids
            
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start,
                end_date=end,
                options=options
            )
            
            response = self.client.transactions_get(request)
            
            transactions = []
            for txn in response.transactions:
                txn_dict = txn.to_dict() if hasattr(txn, 'to_dict') else {}
                
                import json
                from datetime import date, datetime
                def json_serial(obj):
                    if isinstance(obj, (datetime, date)):
                        return obj.isoformat()
                    raise TypeError(f"Type {type(obj)} not serializable")
                
                txn_dict_str = json.dumps(txn_dict, default=json_serial)
                txn_dict = json.loads(txn_dict_str)
                
                personal_finance_category = None
                primary_category = None
                detailed_category = None
                if hasattr(txn, 'personal_finance_category') and txn.personal_finance_category:
                    personal_finance_category = txn.personal_finance_category
                    if hasattr(personal_finance_category, 'primary'):
                        primary_category = personal_finance_category.primary
                    if hasattr(personal_finance_category, 'detailed'):
                        detailed_category = personal_finance_category.detailed
                
                location_city = None
                location_region = None
                location_country = None
                location_address = None
                location_postal_code = None
                if hasattr(txn, 'location') and txn.location:
                    location = txn.location
                    if hasattr(location, 'city'):
                        location_city = location.city
                    if hasattr(location, 'region'):
                        location_region = location.region
                    if hasattr(location, 'country'):
                        location_country = location.country
                    if hasattr(location, 'address'):
                        location_address = location.address
                    if hasattr(location, 'postal_code'):
                        location_postal_code = location.postal_code
                
                merchant_name = None
                if hasattr(txn, 'merchant_name') and txn.merchant_name:
                    merchant_name = txn.merchant_name
                
                transactions.append({
                    "id": txn.transaction_id,
                    "account_id": txn.account_id,
                    "date": txn.date.isoformat() if hasattr(txn.date, "isoformat") else str(txn.date),
                    "authorized_date": txn.authorized_date.isoformat() if hasattr(txn, 'authorized_date') and txn.authorized_date and hasattr(txn.authorized_date, 'isoformat') else None,
                    "name": txn.name,
                    "amount": float(txn.amount),
                    "type": "expense" if txn.amount < 0 else "income",
                    "subtype": None,
                    "category": primary_category or (detailed_category if detailed_category else None),
                    "primary_category": primary_category,
                    "detailed_category": detailed_category,
                    "merchant_name": merchant_name,
                    "location_city": location_city,
                    "location_region": location_region,
                    "location_country": location_country,
                    "location_address": location_address,
                    "location_postal_code": location_postal_code,
                    "iso_currency_code": txn.iso_currency_code if hasattr(txn, 'iso_currency_code') else None,
                    "unofficial_currency_code": txn.unofficial_currency_code if hasattr(txn, 'unofficial_currency_code') else None,
                    "is_pending": txn.pending if hasattr(txn, 'pending') else False,
                    "plaid_data": txn_dict,
                })
            
            return transactions
        except Exception as e:
            raise Exception(f"Failed to get transactions: {str(e)}")
    
    def create_link_token(self, redirect_uri: Optional[str] = None) -> str:
        """Create a link token for Plaid Link"""
        try:
            from plaid.model.link_token_create_request import LinkTokenCreateRequest
            from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
            from plaid.model.products import Products
            from plaid.model.country_code import CountryCode
            
            user = LinkTokenCreateRequestUser(client_user_id="cli-user")
            
            request_kwargs = {
                "products": [Products('investments'), Products('transactions')],
                "client_name": "Finance AI Analyzer",
                "country_codes": [CountryCode('US')],
                "language": 'en',
                "user": user,
            }
            
            if redirect_uri:
                request_kwargs["redirect_uri"] = redirect_uri
            
            request = LinkTokenCreateRequest(**request_kwargs)
            response = self.client.link_token_create(request)
            return response.link_token
        except Exception as e:
            error_msg = str(e)
            if "redirect URI" in error_msg.lower() or "INVALID_FIELD" in error_msg:
                raise Exception(
                    f"Failed to create link token: {error_msg}\n\n"
                    "💡 To fix this:\n"
                    "1. Go to https://dashboard.plaid.com/team/api\n"
                    f"2. Add '{redirect_uri}' to 'Allowed redirect URIs'\n"
                )
            raise Exception(f"Failed to create link token: {error_msg}")
    
    def exchange_public_token(self, public_token: str) -> tuple[str, str]:
        """Exchange a public token for an access token"""
        try:
            from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
            
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            return response.access_token, response.item_id
        except Exception as e:
            raise Exception(f"Failed to exchange public token: {str(e)}")
