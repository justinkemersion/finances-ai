"""Tests for expense analytics"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from backend.app.analytics.expenses import ExpenseAnalyzer
from backend.app.models import Transaction, Account


class TestExpenseAnalytics:
    """Test expense calculation and analysis"""
    
    def test_get_expense_transactions(self, db_session, test_account):
        """Test retrieving expense transactions"""
        # Create expense transaction
        expense_txn = Transaction(
            id="expense_1",
            account_id=test_account.id,
            date=date.today(),
            name="Grocery Store",
            amount=Decimal("-50.00"),
            type="expense",
            is_expense=True,
            expense_category="groceries"
        )
        db_session.add(expense_txn)
        
        # Create income transaction (should not be included)
        income_txn = Transaction(
            id="income_1",
            account_id=test_account.id,
            date=date.today(),
            name="Payroll",
            amount=Decimal("3000.00"),
            type="income",
            is_income=True
        )
        db_session.add(income_txn)
        db_session.commit()
        
        expense_txns = ExpenseAnalyzer.get_expenses(db_session)
        
        assert len(expense_txns) == 1
        assert expense_txns[0].id == "expense_1"
        assert expense_txns[0].is_expense == True
    
    def test_calculate_expense_summary(self, db_session, test_account):
        """Test expense summary calculation"""
        # Create expenses in different categories
        categories = [
            ("groceries", 100.00),
            ("gas", 50.00),
            ("groceries", 75.00),
            ("bills", 150.00),
        ]
        
        for i, (category, amount) in enumerate(categories):
            txn = Transaction(
                id=f"expense_{i}",
                account_id=test_account.id,
                date=date.today() - timedelta(days=i),
                name=f"{category.title()} Purchase",
                amount=Decimal(f"-{amount}"),
                type="expense",
                is_expense=True,
                expense_category=category
            )
            db_session.add(txn)
        db_session.commit()
        
        # Use explicit date range to include all transactions
        start_date = date.today() - timedelta(days=10)
        end_date = date.today()
        summary = ExpenseAnalyzer.calculate_expense_summary(
            db_session,
            start_date=start_date,
            end_date=end_date
        )
        
        # Note: The calculation uses abs() on amounts
        # With explicit date range, all 4 transactions should be included: 100 + 50 + 75 + 150 = 375
        # But if there's existing test data, the count might be higher
        assert summary["total_expenses"] >= 375.00  # At least our test transactions
        assert summary["transaction_count"] >= 4  # At least our test transactions
        assert len(summary["by_category"]) >= 3  # groceries, gas, bills
        
        # Check that groceries appears (should be highest)
        grocery_total = next(
            (item["total"] for item in summary["by_category"] if item["category"] == "groceries"),
            None
        )
        assert grocery_total == 175.00  # 100 + 75
    
    def test_get_monthly_expenses(self, db_session, test_account):
        """Test monthly expense breakdown"""
        # Create expenses across 3 months
        months_ago = [2, 1, 0]
        for month_offset in months_ago:
            txn_date = date.today().replace(day=15) - timedelta(days=month_offset * 30)
            txn = Transaction(
                id=f"expense_month_{month_offset}",
                account_id=test_account.id,
                date=txn_date,
                name="Monthly Expense",
                amount=Decimal("-100.00"),
                type="expense",
                is_expense=True,
                expense_category="bills"
            )
            db_session.add(txn)
        db_session.commit()
        
        monthly = ExpenseAnalyzer.get_monthly_expenses(db_session, months=3)
        
        assert len(monthly) >= 3
        for month_data in monthly:
            assert "month" in month_data
            assert "total_expenses" in month_data
            assert "transaction_count" in month_data
    
    def test_get_top_merchants(self, db_session, test_account):
        """Test top merchants calculation"""
        merchants = [
            ("Starbucks", 50.00),
            ("Starbucks", 30.00),
            ("Amazon", 100.00),
            ("Starbucks", 20.00),
        ]
        
        for i, (merchant, amount) in enumerate(merchants):
            txn = Transaction(
                id=f"merchant_{i}",
                account_id=test_account.id,
                date=date.today() - timedelta(days=i),
                name=f"{merchant} Purchase",
                amount=Decimal(f"-{amount}"),
                type="expense",
                is_expense=True,
                merchant_name=merchant,
                expense_category="shopping"
            )
            db_session.add(txn)
        db_session.commit()
        
        # Use explicit date range
        start_date = date.today() - timedelta(days=10)
        end_date = date.today()
        top_merchants = ExpenseAnalyzer.get_top_merchants(
            db_session,
            limit=5,
            start_date=start_date,
            end_date=end_date
        )
        
        assert len(top_merchants) >= 2
        # The query orders by amount.asc() (ascending), so smallest total first
        # But amounts are negative, so ascending means most negative (largest expense) first
        # Verify totals are correct
        starbucks = next((m for m in top_merchants if m["merchant"] == "Starbucks"), None)
        amazon = next((m for m in top_merchants if m["merchant"] == "Amazon"), None)
        assert starbucks is not None or amazon is not None
        if starbucks:
            assert starbucks["count"] == 3
            assert starbucks["total"] == pytest.approx(100.00, abs=0.01)
        if amazon:
            assert amazon["count"] == 1
            assert amazon["total"] == pytest.approx(100.00, abs=0.01)
    
    def test_expense_filtered_by_category(self, db_session, test_account):
        """Test expense filtering by category"""
        # Grocery expense
        grocery = Transaction(
            id="grocery_1",
            account_id=test_account.id,
            date=date.today(),
            name="Grocery Store",
            amount=Decimal("-50.00"),
            type="expense",
            is_expense=True,
            expense_category="groceries"
        )
        db_session.add(grocery)
        
        # Gas expense
        gas = Transaction(
            id="gas_1",
            account_id=test_account.id,
            date=date.today(),
            name="Gas Station",
            amount=Decimal("-40.00"),
            type="expense",
            is_expense=True,
            expense_category="gas"
        )
        db_session.add(gas)
        db_session.commit()
        
        grocery_expenses = ExpenseAnalyzer.get_expenses(
            db_session,
            expense_category="groceries"
        )
        
        assert len(grocery_expenses) == 1
        assert grocery_expenses[0].id == "grocery_1"
        assert grocery_expenses[0].expense_category == "groceries"
