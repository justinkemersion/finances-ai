"""Teller provider sync implementation"""

from datetime import datetime, date, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from decimal import Decimal

from .base import BaseProviderSync
from .teller_client import TellerClient
from ..models import Account, Holding, Transaction


class TellerSync(BaseProviderSync):
    """Teller implementation of BaseProviderSync"""
    
    def sync_accounts(
        self,
        db: Session,
        access_token: str,
        item_id: str
    ) -> List[Account]:
        """Sync accounts from Teller to database"""
        accounts_data = self.provider_client.get_accounts(access_token)
        synced_accounts = []
        
        for acc_data in accounts_data:
            account = db.query(Account).filter(Account.id == acc_data["id"]).first()
            
            if account:
                account.name = acc_data["name"]
                account.official_name = acc_data.get("official_name")
                account.type = acc_data["type"]
                account.subtype = acc_data.get("subtype")
                account.mask = acc_data.get("mask")
                account.institution_id = acc_data.get("institution_id")
                account.updated_at = datetime.utcnow()
                if acc_data.get("raw_data"):
                    account.plaid_data = acc_data["raw_data"]  # Store Teller data here
            else:
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
        """Sync investment holdings from Teller to database"""
        # Teller doesn't support investment holdings
        return []
    
    def sync_transactions(
        self,
        db: Session,
        access_token: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        sync_investment: bool = True,
        sync_banking: bool = True
    ) -> List[Transaction]:
        """Sync transactions from Teller to database"""
        if start_date is None:
            start_date = date.today() - timedelta(days=30)
        if end_date is None:
            end_date = date.today()
        
        if not sync_banking:
            return []
        
        try:
            transactions_data = self.provider_client.get_transactions(
                access_token,
                start_date.isoformat(),
                end_date.isoformat()
            )
        except Exception:
            return []
        
        return self._process_transactions(db, transactions_data)
    
    def _process_transactions(
        self,
        db: Session,
        transactions_data: List[dict]
    ) -> List[Transaction]:
        """Process and sync transactions to database"""
        synced_transactions = []
        
        for txn_data in transactions_data:
            account = db.query(Account).filter(Account.id == txn_data["account_id"]).first()
            if not account:
                continue
            
            transaction = db.query(Transaction).filter(
                Transaction.id == txn_data["id"]
            ).first()
            
            txn_date = datetime.fromisoformat(txn_data["date"]).date() if isinstance(txn_data["date"], str) else txn_data["date"]
            txn_datetime = None
            if txn_data.get("transaction_datetime"):
                if isinstance(txn_data["transaction_datetime"], str):
                    txn_datetime = datetime.fromisoformat(txn_data["transaction_datetime"].replace('Z', '+00:00'))
                else:
                    txn_datetime = txn_data["transaction_datetime"]
            
            # Classify transaction
            classification = self._classify_transaction(txn_data)
            
            if transaction:
                self._update_transaction(transaction, txn_data, txn_date, txn_datetime, classification)
            else:
                transaction = self._create_transaction(txn_data, txn_date, txn_datetime, classification)
                db.add(transaction)
            
            synced_transactions.append(transaction)
        
        db.commit()
        return synced_transactions
    
    def _classify_transaction(self, txn_data: dict) -> dict:
        """Classify transaction as income, expense, deposit, etc."""
        amount = Decimal(str(txn_data["amount"]))
        name_lower = txn_data.get("name", "").lower()
        
        is_income = False
        is_deposit = False
        is_expense = False
        is_paystub = False
        income_type = None
        expense_category = None
        expense_type = None
        
        if amount > 0:
            is_income = True
            is_deposit = True
            paystub_keywords = ["payroll", "paycheck", "salary", "wage", "pay stub", "direct deposit", "deposit"]
            if any(keyword in name_lower for keyword in paystub_keywords):
                is_paystub = True
                income_type = "salary"
            else:
                income_type = "deposit"
        else:
            is_expense = True
            # Map Teller categories to expense types
            category = txn_data.get("category", "").lower()
            category_map = {
                "food": "food",
                "groceries": "groceries",
                "restaurants": "restaurants",
                "gas": "gas",
                "transportation": "transportation",
                "bills": "bills",
                "utilities": "bills",
                "entertainment": "entertainment",
                "shopping": "shopping",
            }
            expense_category = category_map.get(category, category)
            expense_type = category
        
        return {
            "is_income": is_income,
            "is_deposit": is_deposit,
            "is_expense": is_expense,
            "is_paystub": is_paystub,
            "income_type": income_type,
            "expense_category": expense_category,
            "expense_type": expense_type,
        }
    
    def _update_transaction(
        self,
        transaction: Transaction,
        txn_data: dict,
        txn_date: date,
        txn_datetime: Optional[datetime],
        classification: dict
    ):
        """Update existing transaction"""
        transaction.date = txn_date
        transaction.transaction_datetime = txn_datetime
        transaction.name = txn_data["name"]
        transaction.amount = Decimal(str(txn_data["amount"]))
        transaction.type = txn_data["type"]
        transaction.subtype = txn_data.get("subtype")
        if not transaction.user_category:
            transaction.category = txn_data.get("category")
        transaction.primary_category = txn_data.get("primary_category")
        transaction.detailed_category = txn_data.get("detailed_category")
        transaction.merchant_name = txn_data.get("merchant_name") or transaction.merchant_name
        transaction.is_pending = txn_data.get("is_pending", False)
        transaction.plaid_data = txn_data.get("plaid_data")
        transaction.is_income = classification["is_income"]
        transaction.is_deposit = classification["is_deposit"]
        transaction.is_expense = classification["is_expense"]
        transaction.is_paystub = classification["is_paystub"]
        transaction.income_type = classification["income_type"]
        transaction.expense_category = classification["expense_category"]
        transaction.expense_type = classification["expense_type"]
        transaction.updated_at = datetime.utcnow()
    
    def _create_transaction(
        self,
        txn_data: dict,
        txn_date: date,
        txn_datetime: Optional[datetime],
        classification: dict
    ) -> Transaction:
        """Create new transaction"""
        return Transaction(
            id=txn_data["id"],
            account_id=txn_data["account_id"],
            date=txn_date,
            transaction_datetime=txn_datetime,
            name=txn_data["name"],
            amount=Decimal(str(txn_data["amount"])),
            type=txn_data["type"],
            subtype=txn_data.get("subtype"),
            category=txn_data.get("category"),
            primary_category=txn_data.get("primary_category"),
            detailed_category=txn_data.get("detailed_category"),
            merchant_name=txn_data.get("merchant_name"),
            is_pending=txn_data.get("is_pending", False),
            plaid_data=txn_data.get("plaid_data"),
            is_income=classification["is_income"],
            is_deposit=classification["is_deposit"],
            is_expense=classification["is_expense"],
            is_paystub=classification["is_paystub"],
            income_type=classification["income_type"],
            expense_category=classification["expense_category"],
            expense_type=classification["expense_type"],
        )
    
    def sync_all(
        self,
        db: Session,
        access_token: str,
        item_id: str,
        sync_holdings: bool = True,
        sync_transactions: bool = True
    ) -> dict:
        """Sync all data from Teller"""
        accounts = self.sync_accounts(db, access_token, item_id)
        
        results = {
            "accounts": len(accounts),
            "holdings": 0,  # Teller doesn't support holdings
            "transactions": 0,
        }
        
        if sync_transactions:
            transactions = self.sync_transactions(db, access_token, sync_banking=True)
            results["transactions"] = len(transactions)
        
        return results
