"""Expense analytics for regular banking transactions"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import Transaction, Account


class ExpenseAnalyzer:
    """Analyze expenses and spending patterns"""
    
    @staticmethod
    def get_expenses(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        account_id: Optional[str] = None,
        expense_category: Optional[str] = None
    ) -> List[Transaction]:
        """
        Get all expense transactions
        
        Args:
            db: Database session
            start_date: Start date filter
            end_date: End date filter
            account_id: Filter by account
            expense_category: Filter by expense category
            
        Returns:
            List of expense transactions
        """
        query = db.query(Transaction).filter(Transaction.is_expense == True)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        if expense_category:
            query = query.filter(Transaction.expense_category == expense_category)
        
        return query.order_by(Transaction.date.desc()).all()
    
    @staticmethod
    def calculate_expense_summary(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate expense summary with breakdown by category
        
        Args:
            db: Database session
            start_date: Start date (defaults to start of current month)
            end_date: End date (defaults to today)
            account_id: Filter by account
            
        Returns:
            Dictionary with expense summary
        """
        if start_date is None:
            start_date = date.today().replace(day=1)
        if end_date is None:
            end_date = date.today()
        
        query = db.query(Transaction).filter(
            Transaction.is_expense == True,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        
        # Total expenses
        total_expenses = db.query(func.sum(Transaction.amount)).filter(
            Transaction.is_expense == True,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        if account_id:
            total_expenses = total_expenses.filter(Transaction.account_id == account_id)
        total_expenses = total_expenses.scalar() or Decimal("0")
        
        # Expenses by category
        expenses_by_category = db.query(
            Transaction.expense_category,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.is_expense == True,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        if account_id:
            expenses_by_category = expenses_by_category.filter(Transaction.account_id == account_id)
        expenses_by_category = expenses_by_category.group_by(Transaction.expense_category).all()
        
        # Expenses by primary category (Plaid categories)
        expenses_by_primary = db.query(
            Transaction.primary_category,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.is_expense == True,
            Transaction.date >= start_date,
            Transaction.date <= end_date
        )
        if account_id:
            expenses_by_primary = expenses_by_primary.filter(Transaction.account_id == account_id)
        expenses_by_primary = expenses_by_primary.group_by(Transaction.primary_category).all()
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_expenses": float(abs(total_expenses)),  # Expenses are negative, show as positive
            "transaction_count": db.query(func.count(Transaction.id)).filter(
                Transaction.is_expense == True,
                Transaction.date >= start_date,
                Transaction.date <= end_date
            ).scalar() or 0,
            "by_category": [
                {
                    "category": cat or "uncategorized",
                    "count": count,
                    "total": float(abs(total)) if total else 0.0,
                }
                for cat, count, total in sorted(expenses_by_category, key=lambda x: abs(x[2] or 0), reverse=True)
            ],
            "by_primary_category": [
                {
                    "category": cat or "uncategorized",
                    "count": count,
                    "total": float(abs(total)) if total else 0.0,
                }
                for cat, count, total in sorted(expenses_by_primary, key=lambda x: abs(x[2] or 0), reverse=True)
            ],
        }
    
    @staticmethod
    def get_monthly_expenses(
        db: Session,
        months: int = 12,
        account_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get monthly expense breakdown
        
        Args:
            db: Database session
            months: Number of months to analyze
            account_id: Filter by account
            
        Returns:
            List of monthly expense summaries
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
                Transaction.is_expense == True,
                Transaction.date >= current_date,
                Transaction.date <= month_end
            )
            
            if account_id:
                query = query.filter(Transaction.account_id == account_id)
            
            monthly_expenses = query.scalar() or Decimal("0")
            
            # Count transactions
            count_query = db.query(func.count(Transaction.id)).filter(
                Transaction.is_expense == True,
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
                "total_expenses": float(abs(monthly_expenses)),
                "transaction_count": count,
            })
            
            # Move to next month
            if month_end.month == 12:
                current_date = date(month_end.year + 1, 1, 1)
            else:
                current_date = date(month_end.year, month_end.month + 1, 1)
        
        return monthly_data
    
    @staticmethod
    def get_top_merchants(
        db: Session,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Get top merchants by spending
        
        Args:
            db: Database session
            limit: Number of top merchants to return
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            List of top merchants
        """
        if start_date is None:
            start_date = date.today().replace(day=1)
        if end_date is None:
            end_date = date.today()
        
        query = db.query(
            Transaction.merchant_name,
            func.count(Transaction.id).label('count'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.is_expense == True,
            Transaction.merchant_name.isnot(None),
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ).group_by(Transaction.merchant_name)
        
        results = query.order_by(func.sum(Transaction.amount).asc()).limit(limit).all()
        
        return [
            {
                "merchant": merchant,
                "count": count,
                "total": float(abs(total)) if total else 0.0,
            }
            for merchant, count, total in results
        ]
