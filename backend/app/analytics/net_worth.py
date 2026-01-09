"""Net worth analytics"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import Account, Holding, NetWorthSnapshot


class NetWorthAnalyzer:
    """Calculate and track net worth"""
    
    @staticmethod
    def calculate_current_net_worth(db: Session, as_of_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Calculate current net worth from all accounts and holdings
        
        Args:
            db: Database session
            as_of_date: Date to calculate net worth for (defaults to today)
            
        Returns:
            Dictionary with net worth breakdown
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        # Convert date to datetime for comparison with DateTime column
        from datetime import datetime
        as_of_datetime = datetime.combine(as_of_date, datetime.max.time())
        
        # Get all active accounts
        accounts = db.query(Account).filter(Account.is_active == True).all()
        
        total_assets = Decimal("0")
        total_liabilities = Decimal("0")
        investment_value = Decimal("0")
        cash_value = Decimal("0")
        
        account_breakdown = []
        
        for account in accounts:
            account_value = Decimal("0")
            
            # Get latest holdings for this account
            latest_holdings = db.query(Holding).filter(
                Holding.account_id == account.id,
                Holding.as_of_date <= as_of_datetime
            ).order_by(Holding.as_of_date.desc()).first()
            
            if latest_holdings:
                # Get all holdings for the latest snapshot date
                holdings_date = latest_holdings.as_of_date
                holdings = db.query(Holding).filter(
                    Holding.account_id == account.id,
                    Holding.as_of_date == holdings_date
                ).all()
                
                for holding in holdings:
                    account_value += holding.value or Decimal("0")
            
            # Add to appropriate category
            if account.type == "investment":
                investment_value += account_value
                total_assets += account_value
            elif account.type == "depository":
                cash_value += account_value
                total_assets += account_value
            else:
                # For other account types, assume assets (could be refined)
                total_assets += account_value
            
            account_breakdown.append({
                "account_id": account.id,
                "account_name": account.name,
                "account_type": account.type,
                "value": float(account_value),
            })
        
        net_worth = total_assets - total_liabilities
        
        return {
            "date": as_of_date.isoformat(),
            "total_assets": float(total_assets),
            "total_liabilities": float(total_liabilities),
            "net_worth": float(net_worth),
            "investment_value": float(investment_value),
            "cash_value": float(cash_value),
            "account_count": len(accounts),
            "account_breakdown": account_breakdown,
        }
    
    @staticmethod
    def create_snapshot(db: Session, as_of_date: Optional[date] = None) -> NetWorthSnapshot:
        """
        Create a net worth snapshot for a given date
        
        Args:
            db: Database session
            as_of_date: Date for snapshot (defaults to today)
            
        Returns:
            NetWorthSnapshot object
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        # Check if snapshot already exists
        existing = db.query(NetWorthSnapshot).filter(
            NetWorthSnapshot.date == as_of_date
        ).first()
        
        if existing:
            return existing
        
        # Calculate net worth
        net_worth_data = NetWorthAnalyzer.calculate_current_net_worth(db, as_of_date)
        
        # Create snapshot
        snapshot = NetWorthSnapshot(
            date=as_of_date,
            total_assets=Decimal(str(net_worth_data["total_assets"])),
            total_liabilities=Decimal(str(net_worth_data["total_liabilities"])),
            net_worth=Decimal(str(net_worth_data["net_worth"])),
            investment_value=Decimal(str(net_worth_data["investment_value"])),
            cash_value=Decimal(str(net_worth_data["cash_value"])),
            account_count=net_worth_data["account_count"],
        )
        
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        
        return snapshot
    
    @staticmethod
    def get_net_worth_history(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get net worth history over a date range
        
        Args:
            db: Database session
            start_date: Start date (defaults to 30 days ago)
            end_date: End date (defaults to today)
            
        Returns:
            List of net worth snapshots
        """
        if start_date is None:
            from datetime import timedelta
            start_date = date.today() - timedelta(days=30)
        if end_date is None:
            end_date = date.today()
        
        snapshots = db.query(NetWorthSnapshot).filter(
            NetWorthSnapshot.date >= start_date,
            NetWorthSnapshot.date <= end_date
        ).order_by(NetWorthSnapshot.date.asc()).all()
        
        return [
            {
                "date": snapshot.date.isoformat(),
                "total_assets": float(snapshot.total_assets),
                "total_liabilities": float(snapshot.total_liabilities),
                "net_worth": float(snapshot.net_worth),
                "investment_value": float(snapshot.investment_value) if snapshot.investment_value else None,
                "cash_value": float(snapshot.cash_value) if snapshot.cash_value else None,
                "account_count": snapshot.account_count,
            }
            for snapshot in snapshots
        ]
