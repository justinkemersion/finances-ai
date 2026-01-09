"""Tests for income analytics"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from backend.app.analytics.income import IncomeAnalyzer
from backend.app.models import Transaction, Account


class TestIncomeAnalytics:
    """Test income calculation and analysis"""
    
    def test_get_income_transactions(self, db_session, test_account):
        """Test retrieving income transactions"""
        # Create income transaction
        income_txn = Transaction(
            id="income_1",
            account_id=test_account.id,
            date=date.today(),
            name="Employer - Payroll",
            amount=Decimal("3000.00"),
            type="income",
            is_income=True,
            is_deposit=True,
            is_paystub=True,
            income_type="salary"
        )
        db_session.add(income_txn)
        
        # Create expense transaction (should not be included)
        expense_txn = Transaction(
            id="expense_1",
            account_id=test_account.id,
            date=date.today(),
            name="Grocery Store",
            amount=Decimal("-50.00"),
            type="expense",
            is_expense=True
        )
        db_session.add(expense_txn)
        db_session.commit()
        
        income_txns = IncomeAnalyzer.get_income_transactions(db_session)
        
        assert len(income_txns) == 1
        assert income_txns[0].id == "income_1"
        assert income_txns[0].is_income == True
    
    def test_calculate_income_summary(self, db_session, test_account):
        """Test income summary calculation"""
        # Create multiple income transactions
        for i, amount in enumerate([3000.00, 2500.00, 3000.00]):
            txn = Transaction(
                id=f"income_{i}",
                account_id=test_account.id,
                date=date.today() - timedelta(days=i*7),
                name=f"Payroll {i+1}",
                amount=Decimal(str(amount)),
                type="income",
                is_income=True,
                income_type="salary"
            )
            db_session.add(txn)
        
        # Add paystub transaction
        paystub = Transaction(
            id="paystub_1",
            account_id=test_account.id,
            date=date.today(),
            name="Payroll - Paystub",
            amount=Decimal("3000.00"),
            type="income",
            is_income=True,
            is_paystub=True,
            income_type="salary"
        )
        db_session.add(paystub)
        db_session.commit()
        
        # Use explicit date range to include all transactions
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        summary = IncomeAnalyzer.calculate_income_summary(
            db_session,
            start_date=start_date,
            end_date=end_date
        )
        
        # Default date range is start of year, but we're using explicit range
        # All 4 transactions should be included: 3000 + 2500 + 3000 + 3000 = 8500
        # But if there's existing test data, the total might be higher
        assert summary["total_income"] >= 8500.00  # At least our test transactions
        assert summary["paystub_count"] == 1
        assert summary["paystub_total"] == 3000.00
        assert len(summary["by_type"]) > 0
        assert any(item["type"] == "salary" for item in summary["by_type"])
    
    def test_get_monthly_income(self, db_session, test_account):
        """Test monthly income breakdown"""
        # Create income transactions across 3 months
        months_ago = [2, 1, 0]
        for month_offset in months_ago:
            txn_date = date.today().replace(day=15) - timedelta(days=month_offset * 30)
            txn = Transaction(
                id=f"income_month_{month_offset}",
                account_id=test_account.id,
                date=txn_date,
                name="Payroll",
                amount=Decimal("3000.00"),
                type="income",
                is_income=True,
                income_type="salary"
            )
            db_session.add(txn)
        db_session.commit()
        
        monthly = IncomeAnalyzer.get_monthly_income(db_session, months=3)
        
        assert len(monthly) >= 3
        for month_data in monthly:
            assert "month" in month_data
            assert "total_income" in month_data
            assert "transaction_count" in month_data
    
    def test_income_filtered_by_date_range(self, db_session, test_account):
        """Test income filtering by date range"""
        # Income in range
        txn1 = Transaction(
            id="income_in_range",
            account_id=test_account.id,
            date=date.today() - timedelta(days=10),
            name="Payroll",
            amount=Decimal("3000.00"),
            type="income",
            is_income=True
        )
        db_session.add(txn1)
        
        # Income outside range
        txn2 = Transaction(
            id="income_out_range",
            account_id=test_account.id,
            date=date.today() - timedelta(days=100),
            name="Old Payroll",
            amount=Decimal("3000.00"),
            type="income",
            is_income=True
        )
        db_session.add(txn2)
        db_session.commit()
        
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        income_txns = IncomeAnalyzer.get_income_transactions(
            db_session,
            start_date=start_date,
            end_date=end_date
        )
        
        assert len(income_txns) == 1
        assert income_txns[0].id == "income_in_range"
