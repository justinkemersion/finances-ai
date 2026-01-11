"""Teller provider client implementation using direct HTTP requests"""

from typing import Optional, Dict, Any, List
import json
import os
from datetime import datetime

try:
    import requests
except ImportError:
    raise ImportError(
        "requests library is required for Teller integration. Install with: pip install requests"
    )

from .base import BaseProviderClient
from ..config import config


class TellerClient(BaseProviderClient):
    """Teller implementation of BaseProviderClient using direct HTTP requests"""
    
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
        self.application_id = application_id or config.TELLER_APPLICATION_ID
        self.certificate_path = certificate_path or config.TELLER_CERTIFICATE_PATH
        self.private_key_path = private_key_path or config.TELLER_PRIVATE_KEY_PATH
        self.environment = environment or getattr(config, 'TELLER_ENV', 'sandbox')
        
        if not self.application_id:
            raise ValueError("Teller application_id must be provided")
        if not self.certificate_path:
            raise ValueError("Teller certificate path must be provided (TELLER_CERTIFICATE_PATH)")
        if not os.path.exists(self.certificate_path):
            raise ValueError(
                f"Teller certificate not found at: {self.certificate_path}\n"
                f"Make sure the path is absolute (starts with /) and includes the filename.\n"
                f"Example: /home/user/certs/certificate.pem"
            )
        if not self.private_key_path:
            raise ValueError("Teller private key path must be provided (TELLER_PRIVATE_KEY_PATH)")
        if not os.path.exists(self.private_key_path):
            raise ValueError(
                f"Teller private key not found at: {self.private_key_path}\n"
                f"Make sure the path is absolute (starts with /) and includes the filename.\n"
                f"Example: /home/user/certs/private_key.pem"
            )
        
        # Set base URL based on environment
        # Teller API endpoint: https://api.teller.io/ (for both sandbox and production)
        # Sandbox vs production is determined by the application_id, not the API endpoint
        self.base_url = "https://api.teller.io"
        
        # Create a requests session with mTLS certificate authentication
        # According to Teller docs: mTLS is the primary authentication method
        self.session = requests.Session()
        self.session.cert = (self.certificate_path, self.private_key_path)
        # Don't set Authorization header here - mTLS certificate is the authentication
        # Access tokens use HTTP Basic Auth (set per-request when needed)
        self.session.headers.update({
            "Content-Type": "application/json"
        })
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        access_token: Optional[str] = None,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make an authenticated HTTP request to Teller API
        
        Authentication:
        - mTLS (certificate) is always used (set in session)
        - Access tokens use HTTP Basic Auth (per Teller docs: curl -u ACCESS_TOKEN:)
        - For Connect/enrollment creation, only mTLS is needed (no access token yet)
        """
        url = f"{self.base_url}{endpoint}"
        
        # Prepare request - mTLS is handled by session.cert
        request_kwargs = {
            "method": method,
            "url": url,
            "params": params,
            "json": json_data
        }
        
        # Access tokens use HTTP Basic Auth (not Bearer)
        # Format: requests uses auth=(username, password) for Basic Auth
        if access_token:
            # HTTP Basic Auth: username=access_token, password=empty
            request_kwargs["auth"] = (access_token, "")
        
        try:
            response = self.session.request(**request_kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            raise Exception(f"Teller API error: {error_msg}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Teller API request failed: {str(e)}")
    
    def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """Get all accounts for an access token"""
        try:
            accounts_data = self._make_request("GET", "/accounts", access_token=access_token)
            
            # Teller returns a list of accounts
            if not isinstance(accounts_data, list):
                accounts_data = accounts_data.get("accounts", [])
            
            standardized_accounts = []
            for acc in accounts_data:
                account_id = acc.get("id")
                
                # Get balance for each account
                balance_data = {}
                try:
                    balance_data = self._make_request(
                        "GET",
                        f"/accounts/{account_id}/balances",
                        access_token=access_token
                    )
                except Exception:
                    # Balance endpoint might not be available, use account data
                    balance_data = acc.get("balance", {})
                
                standardized_accounts.append({
                    "id": account_id,
                    "item_id": acc.get("enrollment_id") or acc.get("id"),  # Teller uses enrollment_id
                    "name": acc.get("name", ""),
                    "official_name": acc.get("name", ""),
                    "type": self._map_teller_account_type(acc.get("type", "")),
                    "subtype": acc.get("subtype"),
                    "mask": acc.get("account_number", {}).get("last_4") if isinstance(acc.get("account_number"), dict) else None,
                    "balances": {
                        "available": float(balance_data.get("available", 0)) if balance_data.get("available") else None,
                        "current": float(balance_data.get("ledger", 0) or balance_data.get("current", 0)) if balance_data.get("ledger") or balance_data.get("current") else None,
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
                accounts = self.get_accounts(access_token)
                account_ids = [acc["id"] for acc in accounts]
            
            # Get transactions for each account
            for account_id in account_ids:
                try:
                    params = {
                        "from": start_date,
                        "to": end_date
                    }
                    transactions_data = self._make_request(
                        "GET",
                        f"/accounts/{account_id}/transactions",
                        access_token=access_token,
                        params=params
                    )
                    
                    # Teller returns a list of transactions
                    if not isinstance(transactions_data, list):
                        transactions_data = transactions_data.get("transactions", [])
                    
                    for txn in transactions_data:
                        standardized_txn = self._standardize_transaction(txn, account_id)
                        all_transactions.append(standardized_txn)
                except Exception as e:
                    # Skip accounts that fail
                    continue
            
            return all_transactions
        except Exception as e:
            raise Exception(f"Failed to get transactions: {str(e)}")
    
    def create_link_token(self, redirect_uri: Optional[str] = None) -> str:
        """Create a Connect URL for Teller Connect using REST API"""
        # Teller is a standard REST API - we should make API calls to create Connect sessions
        redirect_uri = redirect_uri or "http://localhost:8080/success"
        
        # Try REST API endpoints to create a Connect session/enrollment
        # Common endpoints: /enrollments, /connect, /authorize
        
        # Try REST API endpoints at https://api.teller.io to create a Connect session/enrollment
        # Based on API root: https://api.teller.io returns {"links":{"accounts":"...","identity":"..."}}
        # We need to find the correct endpoint to create enrollments
        api_endpoints_to_try = [
            # Try common enrollment/connect endpoints
            ("/enrollments", {"redirect_uri": redirect_uri}),
            ("/enrollment", {"redirect_uri": redirect_uri}),  # Singular form
            ("/connect", {"redirect_uri": redirect_uri}),
            ("/authorize", {"redirect_uri": redirect_uri, "response_type": "code"}),
            # Maybe it's under a different path
            ("/v1/enrollments", {"redirect_uri": redirect_uri}),
            ("/v1/enrollment", {"redirect_uri": redirect_uri}),
        ]
        
        last_error = None
        api_errors = []
        for endpoint, payload in api_endpoints_to_try:
            try:
                response = self._make_request(
                    "POST",
                    endpoint,
                    json_data=payload
                )
                # Check for various response formats
                if isinstance(response, dict):
                    # Look for Connect URL in response
                    connect_url = (
                        response.get("url") or 
                        response.get("connect_url") or 
                        response.get("authorization_url") or
                        response.get("enrollment_url") or
                        response.get("link")
                    )
                    if connect_url:
                        return connect_url
                    # Some APIs return the URL directly in a field
                    if "enrollment" in response and isinstance(response["enrollment"], dict):
                        connect_url = response["enrollment"].get("url") or response["enrollment"].get("connect_url")
                        if connect_url:
                            return connect_url
                elif isinstance(response, str) and response.startswith("http"):
                    # API returned URL directly as string
                    return response
            except Exception as e:
                # Store error details for debugging
                error_msg = f"{endpoint}: {str(e)}"
                api_errors.append(error_msg)
                last_error = str(e)
                continue
        
        # If all API calls failed, log the errors (will be shown in console)
        if api_errors:
            import warnings
            warnings.warn(f"Teller API endpoints failed. Errors: {'; '.join(api_errors)}. Falling back to direct URL construction.")
        
        # Fallback: Construct Connect URL directly
        # Based on Teller docs: https://teller.io/connect/{app_id}?redirect_uri={redirect_uri}
        # Format: teller.io (not connect.teller.io), app_id as path parameter
        from urllib.parse import quote
        encoded_redirect_uri = quote(redirect_uri, safe='')
        
        # Correct format: https://teller.io/connect/{app_id}?redirect_uri={redirect_uri}
        connect_base = "https://teller.io"
        connect_url = f"{connect_base}/connect/{self.application_id}?redirect_uri={encoded_redirect_uri}"
        
        return connect_url
    
    def exchange_public_token(self, authorization_code: str) -> tuple[str, str]:
        """
        Exchange authorization code (or loader_id) for access token
        
        Note: According to Teller Connect docs, the accessToken is returned in the 
        enrollment object via the onSuccess callback. Since we're using CLI (not JS SDK),
        we need to retrieve it via API. The loader_id might be used to get enrollment info.
        """
        try:
            # Teller API structure: https://api.teller.io returns {"links":{"accounts":"...","identity":"..."}}
            # The loader_id might need to be used with enrollments endpoint
            # Try different approaches based on Teller API structure
            
            # Approach 1: Check if loader_id can be used to get enrollment details
            # Based on Teller Connect docs, the accessToken is returned in the enrollment object
            # The loader_id might be used to retrieve the enrollment/access token
            if authorization_code.startswith("load_"):
                # This is a loader_id from Teller Connect success page
                # According to Teller docs, enrollments have accessToken in the response
                # Try to get enrollment by loader_id or use it to retrieve access token
                endpoints_to_try = [
                    # Try listing all enrollments - might find the one we just created
                    ("/enrollments", None, "GET"),
                    # Try GET enrollment endpoints - might return accessToken
                    (f"/enrollments/{authorization_code}", None, "GET"),
                    (f"/enrollment/{authorization_code}", None, "GET"),
                    (f"/loaders/{authorization_code}", None, "GET"),
                    (f"/loader/{authorization_code}", None, "GET"),
                ]
            else:
                # This is an authorization code
                endpoints_to_try = [
                    ("/connect/token", {"code": authorization_code}, "POST"),
                    ("/enrollments/token", {"code": authorization_code}, "POST"),
                    ("/token", {"code": authorization_code}, "POST"),
                ]
            
            last_error = None
            response = None
            access_token = None
            
            # Special case: Try using loader_id directly as access token
            # Sometimes the loader_id might actually BE the access token
            if authorization_code.startswith("load_"):
                try:
                    # Try using loader_id as access token to get accounts
                    accounts_response = self._make_request("GET", "/accounts", access_token=authorization_code)
                    # If this works, loader_id IS the access token!
                    if isinstance(accounts_response, list) or (isinstance(accounts_response, dict) and "accounts" in accounts_response):
                        access_token = authorization_code
                        response = accounts_response
                except Exception:
                    # loader_id is not an access token, continue with other methods
                    pass
            
            # If loader_id didn't work as access token, try API endpoints
            if not access_token:
                for endpoint, payload, method in endpoints_to_try:
                    try:
                        if method == "GET":
                            response = self._make_request("GET", endpoint)
                        else:
                            response = self._make_request("POST", endpoint, json_data=payload)
                        
                        # Check for accessToken in various response formats (Teller uses camelCase)
                        access_token = (
                            response.get("accessToken") or  # Teller uses camelCase
                            response.get("access_token") or
                            response.get("token") or
                            (response.get("enrollment", {}) if isinstance(response.get("enrollment"), dict) else {}).get("accessToken") or
                            (response.get("enrollment", {}) if isinstance(response.get("enrollment"), dict) else {}).get("access_token") or
                            (response.get("data", {}) if isinstance(response.get("data"), dict) else {}).get("accessToken") or
                            (response.get("data", {}) if isinstance(response.get("data"), dict) else {}).get("access_token")
                        )
                        
                        # If response is a list of enrollments, check all items
                        if not access_token and isinstance(response, list) and len(response) > 0:
                            # Get the most recent enrollment (check all items)
                            for item in response:
                                if isinstance(item, dict):
                                    item_token = (
                                        item.get("accessToken") or
                                        item.get("access_token") or
                                        (item.get("enrollment", {}) if isinstance(item.get("enrollment"), dict) else {}).get("accessToken")
                                    )
                                    if item_token:
                                        access_token = item_token
                                        break
                        
                        if access_token:
                            # Success - break out of loop
                            break
                    except Exception as e:
                        last_error = str(e)
                        continue
            else:
                # All endpoints failed
                raise Exception(
                    f"All token exchange endpoints failed. Last error: {last_error}\n"
                    f"Tried endpoints: {[ep for ep, _, _ in endpoints_to_try]}\n"
                    f"Check Teller API documentation for the correct token exchange endpoint."
                )
            
            if not access_token:
                # If we still don't have an access token, try listing all enrollments
                # The most recent enrollment should have the access token
                if authorization_code.startswith("load_"):
                    try:
                        # Try to get all enrollments and find the most recent one
                        enrollments_response = self._make_request("GET", "/enrollments")
                        if isinstance(enrollments_response, list) and len(enrollments_response) > 0:
                            # Get the most recent enrollment (assuming last in list or check all)
                            for enrollment in enrollments_response:
                                if isinstance(enrollment, dict):
                                    # Check if this enrollment matches our loader_id or is recent
                                    enrollment_token = (
                                        enrollment.get("accessToken") or
                                        enrollment.get("access_token") or
                                        enrollment.get("token")
                                    )
                                    if enrollment_token:
                                        access_token = enrollment_token
                                        # Get enrollment_id from the enrollment object
                                        enrollment_id = (
                                            enrollment.get("id") or
                                            enrollment.get("enrollment_id") or
                                            enrollment.get("enrollment", {}).get("id") if isinstance(enrollment.get("enrollment"), dict) else None
                                        )
                                        if enrollment_id:
                                            return access_token, enrollment_id
                                        break
                    except Exception as e:
                        pass
                
                if not access_token:
                    raise Exception(
                        f"No access_token found. Response: {response}\n"
                        f"Note: Teller Connect is a JavaScript SDK. The accessToken is returned in the onSuccess callback.\n"
                        f"For CLI usage, you may need to:\n"
                        f"1. Check your Teller Dashboard Activity section for the access token\n"
                        f"2. Or use the Teller API to list enrollments and get the access token\n"
                        f"3. The loader_id ({authorization_code}) might not be directly exchangeable via API"
                    )
            
            # Get enrollment_id from accounts or enrollment object
            enrollment_id = None
            try:
                # Try to get enrollment_id from the response
                if isinstance(response, dict):
                    enrollment_id = (
                        response.get("enrollment", {}).get("id") if isinstance(response.get("enrollment"), dict) else None or
                        response.get("enrollmentId") or
                        response.get("enrollment_id") or
                        response.get("id")
                    )
                
                # If we have access_token, try to get accounts to find enrollment_id
                if not enrollment_id and access_token:
                    accounts = self.get_accounts(access_token)
                    if accounts and len(accounts) > 0:
                        enrollment_id = accounts[0].get("enrollment_id") or accounts[0].get("item_id")
            except Exception:
                pass
            
            # Fallback: use access_token as enrollment_id if we can't find it
            if not enrollment_id:
                enrollment_id = access_token
            
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
        # Handle Teller's amount format (can be dict with value/currency or number)
        amount_value = 0
        currency = "USD"
        if isinstance(txn.get("amount"), dict):
            amount_value = float(txn.get("amount", {}).get("value", 0))
            currency = txn.get("amount", {}).get("currency", "USD")
        else:
            amount_value = float(txn.get("amount", 0))
        
        # Handle date format
        txn_date = txn.get("date")
        txn_datetime = txn.get("timestamp") or txn.get("date")
        
        return {
            "id": txn.get("id"),
            "account_id": account_id,
            "date": txn_date,
            "transaction_datetime": txn_datetime,
            "name": txn.get("description", "") or txn.get("name", ""),
            "amount": amount_value,
            "type": "expense" if amount_value < 0 else "income",
            "subtype": txn.get("type"),
            "category": txn.get("category"),
            "primary_category": txn.get("category"),
            "detailed_category": txn.get("category"),
            "merchant_name": txn.get("merchant", {}).get("name") if isinstance(txn.get("merchant"), dict) else txn.get("merchant"),
            "location_city": None,
            "location_region": None,
            "location_country": None,
            "location_address": None,
            "location_postal_code": None,
            "iso_currency_code": currency,
            "unofficial_currency_code": None,
            "is_pending": txn.get("status") == "pending",
            "plaid_data": json.dumps(txn),  # Store Teller data in plaid_data field for now
        }
