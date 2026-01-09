"""Portfolio performance analytics"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import Account, Holding, NetWorthSnapshot


class PerformanceAnalyzer:
    """Calculate portfolio performance metrics"""
    
    @staticmethod
    def calculate_performance(
        db: Session,
        start_date: date,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Calculate portfolio performance over a time period
        
        Args:
            db: Database session
            start_date: Start date for performance calculation
            end_date: End date (defaults to today)
            
        Returns:
            Dictionary with performance metrics
        """
        if end_date is None:
            end_date = date.today()
        
        # Get net worth snapshots
        start_snapshot = db.query(NetWorthSnapshot).filter(
            NetWorthSnapshot.date == start_date
        ).first()
        
        end_snapshot = db.query(NetWorthSnapshot).filter(
            NetWorthSnapshot.date == end_date
        ).first()
        
        # If snapshots don't exist, create them
        if not start_snapshot:
            from .net_worth import NetWorthAnalyzer
            start_snapshot = NetWorthAnalyzer.create_snapshot(db, start_date)
        
        if not end_snapshot:
            from .net_worth import NetWorthAnalyzer
            end_snapshot = NetWorthAnalyzer.create_snapshot(db, end_date)
        
        # Calculate returns
        start_value = start_snapshot.net_worth
        end_value = end_snapshot.net_worth
        
        absolute_return = end_value - start_value
        percent_return = (absolute_return / start_value * 100) if start_value > 0 else Decimal("0")
        
        # Calculate time period
        days = (end_date - start_date).days
        years = days / 365.25
        
        # Annualized return (if period is less than a year, extrapolate)
        annualized_return = (percent_return / years) if years > 0 else percent_return
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "days": days,
            "start_value": float(start_value),
            "end_value": float(end_value),
            "absolute_return": float(absolute_return),
            "percent_return": float(percent_return),
            "annualized_return": float(annualized_return),
        }
    
    @staticmethod
    def calculate_holdings_performance(
        db: Session,
        account_id: Optional[str] = None,
        as_of_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Calculate performance for individual holdings
        
        Args:
            db: Database session
            account_id: Filter by account (optional)
            as_of_date: Date to calculate performance for (defaults to today)
            
        Returns:
            List of holding performance dictionaries
        """
        if as_of_date is None:
            as_of_date = date.today()
        
        # Get latest holdings
        query = db.query(Holding).filter(
            Holding.as_of_date <= as_of_date
        )
        
        if account_id:
            query = query.filter(Holding.account_id == account_id)
        
        # Get the latest date for each holding
        latest_date = db.query(func.max(Holding.as_of_date)).filter(
            Holding.as_of_date <= as_of_date
        ).scalar()
        
        if not latest_date:
            return []
        
        holdings = db.query(Holding).filter(
            Holding.as_of_date == latest_date
        ).all()
        
        if account_id:
            holdings = [h for h in holdings if h.account_id == account_id]
        
        performance_data = []
        
        for holding in holdings:
            current_value = holding.value or Decimal("0")
            cost_basis = holding.cost_basis or Decimal("0")
            
            # Calculate gain/loss
            gain_loss = current_value - cost_basis
            gain_loss_percent = (gain_loss / cost_basis * 100) if cost_basis > 0 else Decimal("0")
            
            performance_data.append({
                "account_id": holding.account_id,
                "security_id": holding.security_id,
                "ticker": holding.ticker,
                "name": holding.name,
                "quantity": float(holding.quantity),
                "current_price": float(holding.price) if holding.price else None,
                "current_value": float(current_value),
                "cost_basis": float(cost_basis),
                "gain_loss": float(gain_loss),
                "gain_loss_percent": float(gain_loss_percent),
            })
        
        return performance_data
    
    @staticmethod
    def get_monthly_performance(
        db: Session,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get monthly performance for the last N months
        
        Args:
            db: Database session
            months: Number of months to analyze (defaults to 12)
            
        Returns:
            List of monthly performance dictionaries
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        # Get or create snapshots for each month
        monthly_data = []
        
        current_date = start_date.replace(day=1)  # Start of first month
        
        while current_date <= end_date:
            month_end = (current_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            if month_end > end_date:
                month_end = end_date
            
            # Get snapshots for this month
            month_start_snapshot = db.query(NetWorthSnapshot).filter(
                NetWorthSnapshot.date == current_date
            ).first()
            
            month_end_snapshot = db.query(NetWorthSnapshot).filter(
                NetWorthSnapshot.date == month_end
            ).first()
            
            if not month_start_snapshot:
                from .net_worth import NetWorthAnalyzer
                month_start_snapshot = NetWorthAnalyzer.create_snapshot(db, current_date)
            
            if not month_end_snapshot:
                from .net_worth import NetWorthAnalyzer
                month_end_snapshot = NetWorthAnalyzer.create_snapshot(db, month_end)
            
            month_start_value = month_start_snapshot.net_worth
            month_end_value = month_end_snapshot.net_worth
            
            month_return = month_end_value - month_start_value
            month_return_percent = (month_return / month_start_value * 100) if month_start_value > 0 else Decimal("0")
            
            monthly_data.append({
                "month": current_date.strftime("%Y-%m"),
                "start_date": current_date.isoformat(),
                "end_date": month_end.isoformat(),
                "start_value": float(month_start_value),
                "end_value": float(month_end_value),
                "return": float(month_return),
                "return_percent": float(month_return_percent),
            })
            
            # Move to next month
            if month_end.month == 12:
                current_date = date(month_end.year + 1, 1, 1)
            else:
                current_date = date(month_end.year, month_end.month + 1, 1)
        
        return monthly_data
