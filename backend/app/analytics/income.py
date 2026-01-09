"""Income and deposit analytics"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..models import Transaction, Account


class IncomeAnalyzer:
    """Analyze income, deposits, and paystubs"""
    
    @staticmethod
    def get_income_transactions(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        account_id: Optional[str] = None,
        income_type: Optional[str] = None
    ) -> List[Transaction]:
        """
        Get all income transactions
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            account_id: Filter by account
            income_type: Filter by income type
            
        Returns:
            List of income transactions
        """
        query = db.query(Transaction).filter(Transaction.is_income == True)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        if income_type:
            query = query.filter(Transaction.income_type == income_type)
        
        return query.order_by(Transaction.date.desc()).all()
    
    @staticmethod
    def get_deposits(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        account_id: Optional[str] = None
    ) -> List[Transaction]:
        """
        Get all deposit transactions
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            account_id: Filter by account
            
        Returns:
            List of deposit transactions
        """
        query = db.query(Transaction).filter(Transaction.is_deposit == True)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        
        return query.order_by(Transaction.date.desc()).all()
    
    @staticmethod
    def get_paystubs(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        account_id: Optional[str] = None
    ) -> List[Transaction]:
        """
        Get all paystub/payroll transactions
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            account_id: Filter by account
            
        Returns:
            List of paystub transactions
        """
        query = db.query(Transaction).filter(Transaction.is_paystub == True)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        
        return query.order_by(Transaction.date.desc()).all()
    
    @staticmethod
    def calculate_income_summary(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate income summary with breakdown by type
        
        Args:
            db: Database session
            start_date: Start date (defaults to start of current year)
            end_date: End date (defaults to today)
            account_id: Filter by account
            
        Returns:
            Dictionary with income summary
        """
        if start_date is None:
            start_date = date.today().replace(month=1, day=1)
        if end_date is None:
            end_date = date.today()
        
        query = db.query(Transaction).filter(
            Transaction.is_income == True,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        
        # Total income
        total_income = db.query(func.sum(Transaction.amount)).filter(
            Transaction.is_income == True,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        if account_id:
            total_income = total_income.filter(Transaction.account_id == account_id)
        total_income = total_income.scalar() or Decimal("0")
        
        # Income by type
        income_by_type = db.query(
            Transaction.income_type,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.is_income == True,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        if account_id:
            income_by_type = income_by_type.filter(Transaction.account_id == account_id)
        income_by_type = income_by_type.group_by(Transaction.income_type).all()
        
        # Paystub summary
        paystub_query = db.query(
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.is_paystub == True,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        if account_id:
            paystub_query = paystub_query.filter(Transaction.account_id == account_id)
        paystub_stats = paystub_query.first()
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_income": float(total_income),
            "paystub_count": paystub_stats.count if paystub_stats else 0,
            "paystub_total": float(paystub_stats.total) if paystub_stats and paystub_stats.total else 0.0,
            "by_type": [
                {
                    "type": income_type or "unknown",
                    "count": count,
                    "total": float(total) if total else 0.0,
                }
                for income_type, count, total in income_by_type
            ],
        }
    
    @staticmethod
    def get_monthly_income(
        db: Session,
        months: int = 12,
        account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get monthly income breakdown
        
        Args:
            db: Database session
            months: Number of months to analyze
            account_id: Filter by account
            
        Returns:
            List of monthly income summaries
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        monthly_data = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_end = (current_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            if month_end > end_date:
                month_end = end_date
            
            query = db.query(func.sum(Transaction.amount)).filter(
                Transaction.is_income == True,
                Transaction.date >= current_date,
                Transaction.date <= month_end
            )
            
            if account_id:
                query = query.filter(Transaction.account_id == account_id)
            
            monthly_income = query.scalar() or Decimal("0")
            
            # Count transactions
            count_query = db.query(func.count(Transaction.id)).filter(
                Transaction.is_income == True,
                Transaction.date >= current_date,
                Transaction.date <= month_end
            )
            if account_id:
                count_query = count_query.filter(Transaction.account_id == account_id)
            count = count_query.scalar() or 0
            
            monthly_data.append({
                "month": current_date.strftime("%Y-%m"),
                "start_date": current_date.isoformat(),
                "end_date": month_end.isoformat(),
                "total_income": float(monthly_income),
                "transaction_count": count,
            })
            
            # Move to next month
            if month_end.month == 12:
                current_date = date(month_end.year + 1, 1, 1)
            else:
                current_date = date(month_end.year, month_end.month + 1, 1)
        
        return monthly_data
