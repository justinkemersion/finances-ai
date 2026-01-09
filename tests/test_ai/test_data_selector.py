"""Tests for intelligent data selection"""

import pytest
from datetime import date, timedelta, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from backend.app.ai.data_selector import DataSelector
from backend.app.queries.intent_router import QueryIntent
from backend.app.models import Transaction, Account


class TestDataSelector:
    """Test data selection based on query intent"""
    
    def test_select_data_for_expenses_intent(self, db_session, test_account):
        """Test data selection for expense queries"""
        # Add expense transaction
        txn = Transaction(
            id="expense_1",
            account_id=test_account.id,
            date=date.today(),
            name="Grocery Store",
            amount=Decimal("-50.00"),
            type="expense",
            is_expense=True,
            expense_category="groceries"
        )
        db_session.add(txn)
        db_session.commit()
        
        selector = DataSelector(db_session)
        data = selector.select_data("how much did I spend")
        
        assert "expenses" in data
        assert "summary" in data
        assert data["intent"] == QueryIntent.EXPENSES.value
        assert len(data["expenses"]["transactions"]) > 0
    
    def test_select_data_for_income_intent(self, db_session, test_account):
        """Test data selection for income queries"""
        # Add income transaction
        txn = Transaction(
            id="income_1",
            account_id=test_account.id,
            date=date.today(),
            name="Payroll",
            amount=Decimal("3000.00"),
            type="income",
            is_income=True,
            income_type="salary"
        )
        db_session.add(txn)
        db_session.commit()
        
        selector = DataSelector(db_session)
        data = selector.select_data("how much did I earn")
        
        assert "income" in data
        assert "summary" in data
        assert data["intent"] == QueryIntent.INCOME.value
    
    def test_select_data_for_cash_flow_intent(self, db_session, test_account):
        """Test data selection for cash flow queries"""
        selector = DataSelector(db_session)
        data = selector.select_data("what's my cash flow")
        
        assert "income" in data
        assert "expenses" in data
        assert "cash_flow" in data
        assert data["intent"] == QueryIntent.CASH_FLOW.value
    
    def test_select_data_for_net_worth_intent(self, db_session):
        """Test data selection for net worth queries"""
        selector = DataSelector(db_session)
        data = selector.select_data("what is my net worth")
        
        assert "net_worth" in data
        assert "history" in data
        assert data["intent"] == QueryIntent.NET_WORTH.value
    
    def test_select_data_for_performance_intent(self, db_session):
        """Test data selection for performance queries"""
        selector = DataSelector(db_session)
        data = selector.select_data("portfolio performance")
        
        assert "performance" in data
        assert "holdings" in data
        assert data["intent"] == QueryIntent.PERFORMANCE.value
    
    def test_select_data_for_lunch_intent(self, db_session, test_account):
        """Test data selection for lunch queries"""
        # Add lunch transaction
        txn = Transaction(
            id="lunch_1",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 12, 30),
            name="Chipotle",
            amount=Decimal("-12.50"),
            type="expense",
            is_expense=True,
            merchant_name="Chipotle",
            expense_category="restaurants"
        )
        db_session.add(txn)
        db_session.commit()
        
        selector = DataSelector(db_session)
        data = selector.select_data("how much on lunch")
        
        assert "expenses" in data
        assert "lunch_analysis" in data
        assert data["intent"] == QueryIntent.LUNCH.value
    
    def test_select_data_for_merchant_intent(self, db_session, test_account):
        """Test data selection for merchant queries"""
        selector = DataSelector(db_session)
        data = selector.select_data("how much at starbucks")
        
        assert "expenses" in data
        assert "merchants" in data
        assert data["intent"] == QueryIntent.MERCHANT.value
    
    def test_select_data_for_unknown_intent(self, db_session):
        """Test data selection for unknown queries (comprehensive summary)"""
        selector = DataSelector(db_session)
        data = selector.select_data("random question")
        
        assert "summary" in data
        assert "net_worth" in data
        # Should include comprehensive data for general queries
    
    def test_select_data_with_time_range(self, db_session, test_account):
        """Test data selection respects time range from query"""
        # Add transaction in date range
        txn = Transaction(
            id="recent_txn",
            account_id=test_account.id,
            date=date.today() - timedelta(days=5),
            name="Recent Expense",
            amount=Decimal("-30.00"),
            type="expense",
            is_expense=True
        )
        db_session.add(txn)
        db_session.commit()
        
        selector = DataSelector(db_session)
        data = selector.select_data("spending this week")
        
        assert "expenses" in data
        # Should only include transactions from this week
