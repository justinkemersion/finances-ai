"""Export database to formats suitable for LLM analysis"""

import json
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import SessionLocal
from ..models import Account, Holding, Transaction, NetWorthSnapshot
from ..analytics import NetWorthAnalyzer, IncomeAnalyzer, ExpenseAnalyzer, AllocationAnalyzer


def serialize_value(value):
    """Convert database values to JSON-serializable types"""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, '__float__'):
        return float(value)
    return str(value)


def export_accounts(db: Session, include_inactive: bool = False) -> List[Dict[str, Any]]:
    """Export accounts to JSON-serializable format"""
    query = db.query(Account)
    if not include_inactive:
        query = query.filter(Account.is_active == True)
    
    accounts = query.all()
    return [
        {
            "id": acc.id,
            "name": acc.name,
            "official_name": acc.official_name,
            "type": acc.type,
            "subtype": acc.subtype,
            "institution_name": acc.institution_name,
            "mask": acc.mask,
            "is_active": acc.is_active,
            "created_at": serialize_value(acc.created_at),
            "updated_at": serialize_value(acc.updated_at),
        }
        for acc in accounts
    ]


def export_holdings(
    db: Session,
    account_id: Optional[str] = None,
    as_of_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """Export holdings to JSON-serializable format"""
    query = db.query(Holding)
    
    if account_id:
        query = query.filter(Holding.account_id == account_id)
    if as_of_date:
        query = query.filter(Holding.as_of_date <= as_of_date)
    
    holdings = query.all()
    return [
        {
            "account_id": h.account_id,
            "security_id": h.security_id,
            "ticker": h.ticker,
            "name": h.name,
            "quantity": serialize_value(h.quantity),
            "price": serialize_value(h.price),
            "value": serialize_value(h.value),
            "cost_basis": serialize_value(h.cost_basis),
            "as_of_date": serialize_value(h.as_of_date),
            "created_at": serialize_value(h.created_at),
            "updated_at": serialize_value(h.updated_at),
        }
        for h in holdings
    ]


def export_transactions(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    include_investment: bool = True,
    include_banking: bool = True,
    include_pending: bool = True
) -> List[Dict[str, Any]]:
    """Export transactions to JSON-serializable format"""
    query = db.query(Transaction)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if transaction_type:
        query = query.filter(Transaction.type == transaction_type)
    
    # Filter by transaction source
    if not include_investment:
        query = query.filter(~Transaction.type.in_(["buy", "sell", "dividend", "interest", "fee", "cash"]))
    if not include_banking:
        query = query.filter(Transaction.type.in_(["buy", "sell", "dividend", "interest", "fee", "cash"]))
    if not include_pending:
        query = query.filter(Transaction.is_pending == False)
    
    transactions = query.order_by(Transaction.date.desc()).all()
    
    return [
        {
            "id": txn.id,
            "account_id": txn.account_id,
            "date": serialize_value(txn.date),
            "transaction_datetime": serialize_value(txn.transaction_datetime),
            "name": txn.name,
            "amount": serialize_value(txn.amount),
            "currency_code": txn.currency_code,
            "type": txn.type,
            "subtype": txn.subtype,
            "category": txn.category,
            "primary_category": txn.primary_category,
            "detailed_category": txn.detailed_category,
            "merchant_name": txn.merchant_name,
            "location_city": txn.location_city,
            "location_region": txn.location_region,
            "location_country": txn.location_country,
            "is_pending": txn.is_pending,
            "is_income": txn.is_income,
            "is_deposit": txn.is_deposit,
            "is_expense": txn.is_expense,
            "income_type": txn.income_type,
            "expense_category": txn.expense_category,
            "expense_type": txn.expense_type,
            "is_paystub": txn.is_paystub,
            "user_category": txn.user_category,
            "tags": txn.tags,
            "notes": txn.notes,
            "created_at": serialize_value(txn.created_at),
            "updated_at": serialize_value(txn.updated_at),
        }
        for txn in transactions
    ]


def export_net_worth_snapshots(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """Export net worth snapshots to JSON-serializable format"""
    query = db.query(NetWorthSnapshot)
    
    if start_date:
        query = query.filter(NetWorthSnapshot.date >= start_date)
    if end_date:
        query = query.filter(NetWorthSnapshot.date <= end_date)
    
    snapshots = query.order_by(NetWorthSnapshot.date.desc()).all()
    
    return [
        {
            "date": serialize_value(snapshot.date),
            "total_assets": serialize_value(snapshot.total_assets),
            "total_liabilities": serialize_value(snapshot.total_liabilities),
            "net_worth": serialize_value(snapshot.net_worth),
            "investment_value": serialize_value(snapshot.investment_value),
            "cash_value": serialize_value(snapshot.cash_value),
            "created_at": serialize_value(snapshot.created_at),
        }
        for snapshot in snapshots
    ]


def export_summary_statistics(db: Session) -> Dict[str, Any]:
    """Export summary statistics for LLM context"""
    # Current net worth
    net_worth = NetWorthAnalyzer.calculate_current_net_worth(db)
    
    # Income summary
    income_summary = IncomeAnalyzer.calculate_income_summary(db)
    
    # Expense summary
    expense_summary = ExpenseAnalyzer.calculate_expense_summary(db)
    
    # Allocation
    allocation = AllocationAnalyzer.calculate_allocation(db)
    
    # Account counts
    total_accounts = db.query(func.count(Account.id)).filter(Account.is_active == True).scalar() or 0
    total_holdings = db.query(func.count(Holding.id)).scalar() or 0
    total_transactions = db.query(func.count(Transaction.id)).scalar() or 0
    
    # Date ranges
    oldest_txn = db.query(func.min(Transaction.date)).scalar()
    newest_txn = db.query(func.max(Transaction.date)).scalar()
    
    return {
        "export_date": datetime.utcnow().isoformat(),
        "summary": {
            "accounts": total_accounts,
            "holdings": total_holdings,
            "transactions": total_transactions,
            "transaction_date_range": {
                "oldest": serialize_value(oldest_txn),
                "newest": serialize_value(newest_txn),
            }
        },
        "net_worth": {
            "total_assets": float(net_worth["total_assets"]),
            "total_liabilities": float(net_worth["total_liabilities"]),
            "net_worth": float(net_worth["net_worth"]),
            "investment_value": float(net_worth["investment_value"]),
            "cash_value": float(net_worth["cash_value"]),
        },
        "income": {
            "total_income": float(income_summary["total_income"]),
            "paystub_count": income_summary["paystub_count"],
            "paystub_total": float(income_summary["paystub_total"]),
            "by_type": [
                {
                    "type": item["type"],
                    "count": item["count"],
                    "total": float(item["total"]),
                }
                for item in income_summary["by_type"]
            ]
        },
        "expenses": {
            "total_expenses": expense_summary["total_expenses"],
            "transaction_count": expense_summary["transaction_count"],
            "by_category": expense_summary["by_category"][:10],  # Top 10
        },
        "portfolio": {
            "total_value": float(allocation["total_value"]),
            "holdings_count": len(allocation["by_security"]),
            "top_holdings": [
                {
                    "ticker": h.get("ticker"),
                    "name": h.get("name"),
                    "value": float(h["value"]),
                    "allocation_percent": float(h["allocation_percent"]),
                }
                for h in allocation["by_security"][:10]  # Top 10
            ]
        }
    }


def export_to_json(
    output_path: str,
    include_accounts: bool = True,
    include_holdings: bool = True,
    include_transactions: bool = True,
    include_net_worth: bool = True,
    include_summary: bool = True,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    account_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    include_investment_txns: bool = True,
    include_banking_txns: bool = True,
    include_pending: bool = True,
    include_inactive_accounts: bool = False
) -> str:
    """
    Export database to JSON format suitable for LLM analysis
    
    Args:
        output_path: Path to output JSON file
        include_accounts: Include accounts data
        include_holdings: Include holdings data
        include_transactions: Include transactions data
        include_net_worth: Include net worth snapshots
        include_summary: Include summary statistics
        start_date: Filter transactions by start date
        end_date: Filter transactions by end date
        account_id: Filter by account ID
        transaction_type: Filter by transaction type
        include_investment_txns: Include investment transactions
        include_banking_txns: Include banking transactions
        include_pending: Include pending transactions
        include_inactive_accounts: Include inactive accounts
        
    Returns:
        Path to exported file
    """
    db = SessionLocal()
    
    try:
        export_data = {
            "metadata": {
                "export_date": datetime.utcnow().isoformat(),
                "export_version": "1.0",
                "filters": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "account_id": account_id,
                    "transaction_type": transaction_type,
                    "include_investment_txns": include_investment_txns,
                    "include_banking_txns": include_banking_txns,
                    "include_pending": include_pending,
                }
            }
        }
        
        if include_summary:
            export_data["summary"] = export_summary_statistics(db)
        
        if include_accounts:
            export_data["accounts"] = export_accounts(db, include_inactive=include_inactive_accounts)
        
        if include_holdings:
            export_data["holdings"] = export_holdings(db, account_id=account_id)
        
        if include_transactions:
            export_data["transactions"] = export_transactions(
                db,
                start_date=start_date,
                end_date=end_date,
                account_id=account_id,
                transaction_type=transaction_type,
                include_investment=include_investment_txns,
                include_banking=include_banking_txns,
                include_pending=include_pending
            )
        
        if include_net_worth:
            export_data["net_worth_snapshots"] = export_net_worth_snapshots(
                db,
                start_date=start_date,
                end_date=end_date
            )
        
        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return str(output_file.absolute())
    
    finally:
        db.close()
