"""Plaid data synchronization jobs"""

from datetime import datetime, date, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from decimal import Decimal

from ..database import get_db
from ..models import Account, Holding, Transaction, NetWorthSnapshot
from .client import PlaidClient


class PlaidSync:
    """Handles syncing data from Plaid to the database"""
    
    def __init__(self, plaid_client: Optional[PlaidClient] = None):
        """
        Initialize sync handler
        
        Args:
            plaid_client: Plaid client instance (creates new one if not provided)
        """
        self.plaid_client = plaid_client or PlaidClient()
    
    def sync_accounts(self, db: Session, access_token: str, item_id: str) -> List[Account]:
        """
        Sync accounts from Plaid to database
        
        Args:
            db: Database session
            access_token: Plaid access token
            item_id: Plaid item ID
            
        Returns:
            List of synced Account objects
        """
        accounts_data = self.plaid_client.get_accounts(access_token)
        synced_accounts = []
        
        for acc_data in accounts_data:
            # Check if account exists
            account = db.query(Account).filter(Account.id == acc_data["id"]).first()
            
            if account:
                # Update existing account
                account.name = acc_data["name"]
                account.official_name = acc_data.get("official_name")
                account.type = acc_data["type"]
                account.subtype = acc_data.get("subtype")
                account.mask = acc_data.get("mask")
                account.institution_id = acc_data.get("institution_id")
                account.updated_at = datetime.utcnow()
                if acc_data.get("raw_data"):
                    account.plaid_data = acc_data["raw_data"]
            else:
                # Create new account
                account = Account(
                    id=acc_data["id"],
                    item_id=item_id,
                    name=acc_data["name"],
                    official_name=acc_data.get("official_name"),
                    type=acc_data["type"],
                    subtype=acc_data.get("subtype"),
                    mask=acc_data.get("mask"),
                    institution_id=acc_data.get("institution_id"),
                    plaid_data=acc_data.get("raw_data"),
                )
                db.add(account)
            
            synced_accounts.append(account)
        
        db.commit()
        return synced_accounts
    
    def sync_holdings(
        self,
        db: Session,
        access_token: str,
        as_of_date: Optional[date] = None
    ) -> List[Holding]:
        """
        Sync investment holdings from Plaid to database
        
        Args:
            db: Database session
            access_token: Plaid access token
            as_of_date: Date for the holdings snapshot (defaults to today)
            
        Returns:
            List of synced Holding objects
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        holdings_data = self.plaid_client.get_investment_holdings(access_token)
        synced_holdings = []
        
        for account_id, holdings_list in holdings_data["holdings"].items():
            # Verify account exists
            account = db.query(Account).filter(Account.id == account_id).first()
            if not account:
                continue  # Skip if account doesn't exist
            
            for holding_data in holdings_list:
                security = holding_data.get("security", {})
                
                # Check if holding exists (primary key is account_id + security_id)
                holding = db.query(Holding).filter(
                    Holding.account_id == account_id,
                    Holding.security_id == holding_data["security_id"]
                ).first()
                
                if holding:
                    # Update existing holding
                    holding.quantity = Decimal(str(holding_data["quantity"]))
                    holding.price = Decimal(str(holding_data["price"])) if holding_data.get("price") else None
                    holding.value = Decimal(str(holding_data["value"])) if holding_data.get("value") else Decimal("0")
                    holding.cost_basis = Decimal(str(holding_data["cost_basis"])) if holding_data.get("cost_basis") else None
                    holding.as_of_date = as_of_date  # Update the snapshot date
                    holding.updated_at = datetime.utcnow()
                else:
                    # Create new holding
                    holding = Holding(
                        account_id=account_id,
                        security_id=holding_data["security_id"],
                        name=security.get("name", ""),
                        ticker=security.get("ticker"),
                        cusip=security.get("cusip"),
                        isin=security.get("isin"),
                        sedol=security.get("sedol"),
                        security_type=security.get("type"),
                        quantity=Decimal(str(holding_data["quantity"])),
                        price=Decimal(str(holding_data["price"])) if holding_data.get("price") else None,
                        value=Decimal(str(holding_data["value"])) if holding_data.get("value") else Decimal("0"),
                        cost_basis=Decimal(str(holding_data["cost_basis"])) if holding_data.get("cost_basis") else None,
                        as_of_date=as_of_date,
                    )
                    db.add(holding)
                
                synced_holdings.append(holding)
        
        db.commit()
        return synced_holdings
    
    def sync_transactions(
        self,
        db: Session,
        access_token: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sync_investment: bool = True,
        sync_banking: bool = True
    ) -> List[Transaction]:
        """
        Sync transactions from Plaid to database (both investment and banking)
        
        Args:
            db: Database session
            access_token: Plaid access token
            start_date: Start date for transactions (defaults to 30 days ago)
            end_date: End date for transactions (defaults to today)
            sync_investment: Whether to sync investment transactions
            sync_banking: Whether to sync regular banking transactions
            
        Returns:
            List of synced Transaction objects
        """
        if start_date is None:
            start_date = date.today() - timedelta(days=30)
        if end_date is None:
            end_date = date.today()
        
        all_transactions_data = []
        
        # Sync investment transactions
        if sync_investment:
            try:
                investment_txns = self.plaid_client.get_investment_transactions(
                    access_token,
                    start_date.isoformat(),
                    end_date.isoformat()
                )
                all_transactions_data.extend(investment_txns)
            except Exception as e:
                # If investment transactions fail (e.g., no investment accounts), continue
                pass
        
        # Sync regular banking transactions
        if sync_banking:
            try:
                # Get all accounts to find checking/savings accounts
                accounts_data = self.plaid_client.get_accounts(access_token)
                banking_account_ids = [
                    acc["id"] for acc in accounts_data
                    if acc["type"] in ["depository", "credit"]
                ]
                
                if banking_account_ids:
                    banking_txns = self.plaid_client.get_transactions(
                        access_token,
                        start_date.isoformat(),
                        end_date.isoformat(),
                        account_ids=banking_account_ids
                    )
                    all_transactions_data.extend(banking_txns)
            except Exception as e:
                # If banking transactions fail, continue
                pass
        
        transactions_data = all_transactions_data
        
        synced_transactions = []
        
        for txn_data in transactions_data:
            # Verify account exists
            account = db.query(Account).filter(Account.id == txn_data["account_id"]).first()
            if not account:
                continue  # Skip if account doesn't exist
            
            # Check if transaction exists
            transaction = db.query(Transaction).filter(
                Transaction.id == txn_data["id"]
            ).first()
            
            # Parse dates
            txn_date = datetime.fromisoformat(txn_data["date"]).date() if isinstance(txn_data["date"], str) else txn_data["date"]
            txn_datetime = None
            if txn_data.get("transaction_datetime"):
                if isinstance(txn_data["transaction_datetime"], str):
                    txn_datetime = datetime.fromisoformat(txn_data["transaction_datetime"].replace('Z', '+00:00'))
                else:
                    txn_datetime = txn_data["transaction_datetime"]
            
            # Determine if cancelled
            is_cancelled = bool(txn_data.get("cancel_transaction_id"))
            
            # Detect income/deposit/expense transactions
            txn_type = txn_data.get("type", "").lower()
            txn_subtype = txn_data.get("subtype", "").lower() if txn_data.get("subtype") else ""
            amount = Decimal(str(txn_data["amount"]))
            primary_category = txn_data.get("primary_category")
            detailed_category = txn_data.get("detailed_category")
            
            is_income = False
            is_deposit = False
            is_expense = False
            is_paystub = False
            income_type = None
            expense_category = None
            expense_type = None
            
            # For regular banking transactions: positive = income/deposit, negative = expense
            # For investment transactions: use type/subtype
            if txn_type in ["expense", "income"]:
                # Regular banking transaction
                if amount > 0:
                    is_income = True
                    is_deposit = True
                    # Check for paystub
                    name_lower = txn_data.get("name", "").lower()
                    paystub_keywords = ["payroll", "paycheck", "salary", "wage", "pay stub", "direct deposit", "deposit"]
                    if any(keyword in name_lower for keyword in paystub_keywords):
                        is_paystub = True
                        income_type = "salary"
                    else:
                        income_type = "deposit"
                else:
                    is_expense = True
                    # Map Plaid categories to expense types
                    if primary_category:
                        expense_type = primary_category
                        # Map to friendly expense categories
                        category_map = {
                            "FOOD_AND_DRINK": "food",
                            "GENERAL_MERCHANDISE": "shopping",
                            "GENERAL_SERVICES": "services",
                            "GOVERNMENT_AND_NON_PROFIT": "government",
                            "TRANSPORTATION": "transportation",
                            "TRAVEL": "travel",
                            "RENT_AND_UTILITIES": "bills",
                            "PERSONAL_CARE": "personal",
                            "ENTERTAINMENT": "entertainment",
                            "GAS_STATIONS": "gas",
                            "GROCERIES": "groceries",
                        }
                        # Check detailed category first for specific items
                        if detailed_category:
                            if "GROCERIES" in detailed_category:
                                expense_category = "groceries"
                            elif "GAS_STATIONS" in detailed_category:
                                expense_category = "gas"
                            elif "UTILITIES" in detailed_category or "RENT" in detailed_category:
                                expense_category = "bills"
                            elif "RESTAURANTS" in detailed_category:
                                expense_category = "restaurants"
                            else:
                                expense_category = category_map.get(primary_category, primary_category.lower())
                        else:
                            expense_category = category_map.get(primary_category, primary_category.lower())
            # Investment income types
            elif txn_type in ["dividend", "interest", "distribution"]:
                is_income = True
                income_type = txn_type
            elif txn_subtype in ["dividend", "interest", "long_term_capital_gain", "short_term_capital_gain"]:
                is_income = True
                income_type = txn_subtype
            # Investment expenses (fees, etc.)
            elif txn_type in ["fee"]:
                is_expense = True
                expense_category = "fees"
                expense_type = "investment"
            # Deposits (positive amounts that aren't income)
            elif amount > 0 and txn_type in ["deposit", "transfer"]:
                is_deposit = True
            # Paystub detection (look for payroll-related keywords in name)
            elif amount > 0:
                name_lower = txn_data.get("name", "").lower()
                paystub_keywords = ["payroll", "paycheck", "salary", "wage", "pay stub", "direct deposit"]
                if any(keyword in name_lower for keyword in paystub_keywords):
                    is_paystub = True
                    is_income = True
                    is_deposit = True
                    income_type = "salary"
            
            if transaction:
                # Update existing transaction (preserve user-defined fields)
                transaction.date = txn_date
                transaction.transaction_datetime = txn_datetime
                transaction.name = txn_data["name"]
                transaction.amount = Decimal(str(txn_data["amount"]))
                transaction.type = txn_data["type"]
                transaction.subtype = txn_data.get("subtype")
                # Don't overwrite user_category if it exists
                if not transaction.user_category:
                    transaction.category = txn_data.get("detailed_category") or txn_data.get("primary_category") or txn_data.get("subtype")
                transaction.primary_category = txn_data.get("primary_category")
                transaction.detailed_category = txn_data.get("detailed_category")
                transaction.quantity = Decimal(str(txn_data["quantity"])) if txn_data.get("quantity") else None
                transaction.price = Decimal(str(txn_data["price"])) if txn_data.get("price") else None
                transaction.fees = Decimal(str(txn_data["fees"])) if txn_data.get("fees") else None
                transaction.security_id = txn_data.get("security_id")
                transaction.merchant_name = txn_data.get("merchant_name") or transaction.merchant_name
                transaction.location_city = txn_data.get("location_city") or transaction.location_city
                transaction.location_region = txn_data.get("location_region") or transaction.location_region
                transaction.location_country = txn_data.get("location_country") or transaction.location_country
                transaction.location_address = txn_data.get("location_address") or transaction.location_address
                transaction.location_postal_code = txn_data.get("location_postal_code") or transaction.location_postal_code
                transaction.iso_currency_code = txn_data.get("iso_currency_code")
                transaction.unofficial_currency_code = txn_data.get("unofficial_currency_code")
                transaction.cancel_transaction_id = txn_data.get("cancel_transaction_id")
                transaction.is_cancelled = is_cancelled
                transaction.is_pending = txn_data.get("is_pending", False)
                transaction.plaid_data = txn_data.get("plaid_data")
                # Income/deposit/expense classification
                transaction.is_income = is_income
                transaction.is_deposit = is_deposit
                transaction.is_expense = is_expense
                transaction.is_paystub = is_paystub
                transaction.income_type = income_type
                transaction.expense_category = expense_category
                transaction.expense_type = expense_type
                transaction.updated_at = datetime.utcnow()
            else:
                # Create new transaction
                transaction = Transaction(
                    id=txn_data["id"],
                    account_id=txn_data["account_id"],
                    date=txn_date,
                    transaction_datetime=txn_datetime,
                    name=txn_data["name"],
                    amount=Decimal(str(txn_data["amount"])),
                    type=txn_data["type"],
                    subtype=txn_data.get("subtype"),
                    category=txn_data.get("detailed_category") or txn_data.get("primary_category") or txn_data.get("subtype"),
                    primary_category=txn_data.get("primary_category"),
                    detailed_category=txn_data.get("detailed_category"),
                    quantity=Decimal(str(txn_data["quantity"])) if txn_data.get("quantity") else None,
                    price=Decimal(str(txn_data["price"])) if txn_data.get("price") else None,
                    fees=Decimal(str(txn_data["fees"])) if txn_data.get("fees") else None,
                    security_id=txn_data.get("security_id"),
                    ticker=None,  # Would need to look up from security
                    merchant_name=txn_data.get("merchant_name"),
                    location_city=txn_data.get("location_city"),
                    location_region=txn_data.get("location_region"),
                    location_country=txn_data.get("location_country"),
                    location_address=txn_data.get("location_address"),
                    location_postal_code=txn_data.get("location_postal_code"),
                    iso_currency_code=txn_data.get("iso_currency_code"),
                    unofficial_currency_code=txn_data.get("unofficial_currency_code"),
                    cancel_transaction_id=txn_data.get("cancel_transaction_id"),
                    is_cancelled=is_cancelled,
                    is_pending=txn_data.get("is_pending", False),
                    plaid_data=txn_data.get("plaid_data"),
                    # Income/deposit/expense classification
                    is_income=is_income,
                    is_deposit=is_deposit,
                    is_expense=is_expense,
                    is_paystub=is_paystub,
                    income_type=income_type,
                    expense_category=expense_category,
                    expense_type=expense_type,
                )
                db.add(transaction)
            
            synced_transactions.append(transaction)
        
        db.commit()
        return synced_transactions
    
    def sync_all(
        self,
        db: Session,
        access_token: str,
        item_id: str,
        sync_holdings: bool = True,
        sync_transactions: bool = True
    ) -> dict:
        """
        Sync all data from Plaid (accounts, holdings, transactions)
        
        Args:
            db: Database session
            access_token: Plaid access token
            item_id: Plaid item ID
            sync_holdings: Whether to sync holdings
            sync_transactions: Whether to sync transactions
            
        Returns:
            Dictionary with sync results
        """
        accounts = self.sync_accounts(db, access_token, item_id)
        
        results = {
            "accounts": len(accounts),
            "holdings": 0,
            "transactions": 0,
        }
        
        if sync_holdings:
            holdings = self.sync_holdings(db, access_token)
            results["holdings"] = len(holdings)
        
        if sync_transactions:
            transactions = self.sync_transactions(db, access_token)
            results["transactions"] = len(transactions)
        
        return results
