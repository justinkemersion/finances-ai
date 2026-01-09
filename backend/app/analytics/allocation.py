"""Portfolio allocation analytics"""

from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict

from ..models import Account, Holding


class AllocationAnalyzer:
    """Calculate portfolio allocation metrics"""
    
    @staticmethod
    def calculate_allocation(
        db: Session,
        account_id: Optional[str] = None,
        as_of_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate portfolio allocation by security, sector, and account
        
        Args:
            db: Database session
            account_id: Filter by account (optional)
            as_of_date: Date to calculate allocation for (defaults to today)
            
        Returns:
            Dictionary with allocation breakdowns
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        # Get latest holdings
        query = db.query(Holding).filter(
            Holding.as_of_date <= as_of_date
        )
        
        if account_id:
            query = query.filter(Holding.account_id == account_id)
        
        # Get the latest date
        latest_date = db.query(func.max(Holding.as_of_date)).filter(
            Holding.as_of_date <= as_of_date
        ).scalar()
        
        if not latest_date:
            return {
                "total_value": 0,
                "by_security": [],
                "by_account": [],
                "by_type": [],
            }
        
        holdings = db.query(Holding).filter(
            Holding.as_of_date == latest_date
        ).all()
        
        if account_id:
            holdings = [h for h in holdings if h.account_id == account_id]
        
        total_value = sum(h.value or Decimal("0") for h in holdings)
        
        # Allocation by security
        by_security = defaultdict(lambda: {"value": Decimal("0"), "quantity": Decimal("0"), "ticker": None, "name": None})
        by_account = defaultdict(lambda: {"value": Decimal("0"), "holdings": []})
        by_type = defaultdict(lambda: {"value": Decimal("0"), "count": 0})
        
        for holding in holdings:
            value = holding.value or Decimal("0")
            security_key = holding.security_id or holding.ticker or holding.name
            
            # By security
            by_security[security_key]["value"] += value
            by_security[security_key]["quantity"] += holding.quantity
            if not by_security[security_key]["ticker"]:
                by_security[security_key]["ticker"] = holding.ticker
            if not by_security[security_key]["name"]:
                by_security[security_key]["name"] = holding.name
            
            # By account
            by_account[holding.account_id]["value"] += value
            by_account[holding.account_id]["holdings"].append({
                "security_id": holding.security_id,
                "ticker": holding.ticker,
                "name": holding.name,
                "value": float(value),
            })
            
            # By type
            security_type = holding.security_type or "unknown"
            by_type[security_type]["value"] += value
            by_type[security_type]["count"] += 1
        
        # Convert to lists with percentages
        by_security_list = [
            {
                "security_id": key,
                "ticker": data["ticker"],
                "name": data["name"],
                "value": float(data["value"]),
                "quantity": float(data["quantity"]),
                "allocation_percent": float((data["value"] / total_value * 100) if total_value > 0 else 0),
            }
            for key, data in sorted(by_security.items(), key=lambda x: x[1]["value"], reverse=True)
        ]
        
        by_account_list = []
        for acc_id, data in by_account.items():
            account = db.query(Account).filter(Account.id == acc_id).first()
            by_account_list.append({
                "account_id": acc_id,
                "account_name": account.name if account else acc_id,
                "value": float(data["value"]),
                "allocation_percent": float((data["value"] / total_value * 100) if total_value > 0 else 0),
                "holdings_count": len(data["holdings"]),
            })
        by_account_list.sort(key=lambda x: x["value"], reverse=True)
        
        by_type_list = [
            {
                "type": key,
                "value": float(data["value"]),
                "allocation_percent": float((data["value"] / total_value * 100) if total_value > 0 else 0),
                "count": data["count"],
            }
            for key, data in sorted(by_type.items(), key=lambda x: x[1]["value"], reverse=True)
        ]
        
        return {
            "as_of_date": as_of_date.isoformat(),
            "total_value": float(total_value),
            "by_security": by_security_list,
            "by_account": by_account_list,
            "by_type": by_type_list,
        }
    
    @staticmethod
    def get_top_holdings(
        db: Session,
        limit: int = 10,
        account_id: Optional[str] = None,
        as_of_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top N holdings by value
        
        Args:
            db: Database session
            limit: Number of top holdings to return
            account_id: Filter by account (optional)
            as_of_date: Date to calculate for (defaults to today)
            
        Returns:
            List of top holdings
        """
        allocation = AllocationAnalyzer.calculate_allocation(db, account_id, as_of_date)
        return allocation["by_security"][:limit]
    
    @staticmethod
    def get_account_allocation(
        db: Session,
        as_of_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get allocation breakdown by account
        
        Args:
            db: Database session
            as_of_date: Date to calculate for (defaults to today)
            
        Returns:
            List of account allocations
        """
        allocation = AllocationAnalyzer.calculate_allocation(db, as_of_date=as_of_date)
        return allocation["by_account"]
