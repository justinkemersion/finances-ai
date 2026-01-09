"""Tests for query handlers (routing and execution)"""

import pytest
from datetime import date, timedelta, datetime
from decimal import Decimal

from backend.app.queries.handlers import QueryHandler
from backend.app.queries.intent_router import QueryIntent
from backend.app.models import Account, Transaction, Holding


class TestQueryHandler:
    """Test query handler routing and execution"""
    
    def test_handle_net_worth_query(self, db_session, test_account):
        """Test net worth query handling"""
        from backend.app.models import Holding
        from datetime import datetime
        
        # Add a holding to represent account value
        holding = Holding(
            account_id=test_account.id,
            security_id="cash",
            ticker="CASH",
            name="Cash Balance",
            quantity=Decimal("1.0"),
            price=Decimal("5000.00"),
            value=Decimal("5000.00"),
            cost_basis=Decimal("5000.00"),
            as_of_date=datetime.combine(date.today(), datetime.min.time())
        )
        db_session.add(holding)
        db_session.commit()
        
        handler = QueryHandler(db_session)
        result = handler.handle_query("what is my net worth")
        
        assert result is not None
        assert "net_worth" in result or "Net Worth" in str(result)
    
    def test_handle_income_query(self, db_session, test_account):
        """Test income query handling"""
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
        
        handler = QueryHandler(db_session)
        result = handler.handle_query("how much did I earn")
        
        assert result is not None
        assert "income" in str(result).lower() or "earn" in str(result).lower()
    
    def test_handle_expenses_query(self, db_session, test_account):
        """Test expenses query handling"""
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
        
        handler = QueryHandler(db_session)
        result = handler.handle_query("how much did I spend")
        
        assert result is not None
        assert "expense" in str(result).lower() or "spend" in str(result).lower()
    
    def test_handle_spending_category_query(self, db_session, test_account):
        """Test category-specific spending query"""
        # Add beer transaction
        txn = Transaction(
            id="beer_1",
            account_id=test_account.id,
            date=date.today(),
            name="Bar Purchase",
            amount=Decimal("-25.00"),
            type="expense",
            is_expense=True,
            expense_category="alcohol",
            merchant_name="Local Bar"
        )
        db_session.add(txn)
        db_session.commit()
        
        handler = QueryHandler(db_session)
        result = handler.handle_query("how much did I spend on beer")
        
        assert result is not None
        assert "beer" in str(result).lower() or "alcohol" in str(result).lower()
    
    def test_handle_lunch_query(self, db_session, test_account):
        """Test lunch detection query"""
        # Add lunch transaction
        txn = Transaction(
            id="lunch_1",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 12, 30),  # Lunch time
            name="Chipotle",
            amount=Decimal("-12.50"),
            type="expense",
            is_expense=True,
            merchant_name="Chipotle",
            expense_category="restaurants"
        )
        db_session.add(txn)
        db_session.commit()
        
        handler = QueryHandler(db_session)
        result = handler.handle_query("how much on lunch")
        
        assert result is not None
        assert "lunch" in str(result).lower()
    
    def test_handle_merchant_query(self, db_session, test_account):
        """Test merchant-specific query"""
        # Add merchant transaction
        txn = Transaction(
            id="merchant_1",
            account_id=test_account.id,
            date=date.today(),
            name="Starbucks Purchase",
            amount=Decimal("-5.50"),
            type="expense",
            is_expense=True,
            merchant_name="Starbucks",
            expense_category="food"
        )
        db_session.add(txn)
        db_session.commit()
        
        handler = QueryHandler(db_session)
        result = handler.handle_query("how much at starbucks")
        
        assert result is not None
        assert "starbucks" in str(result).lower()
    
    def test_handle_performance_query(self, db_session):
        """Test performance query handling"""
        from backend.app.models import NetWorthSnapshot
        
        # Add performance snapshots
        start_snapshot = NetWorthSnapshot(
            date=date.today() - timedelta(days=30),
            total_assets=Decimal("10000.00"),
            total_liabilities=Decimal("0.00"),
            net_worth=Decimal("10000.00"),
            investment_value=Decimal("10000.00"),
            cash_value=Decimal("0.00"),
            account_count=1
        )
        db_session.add(start_snapshot)
        
        end_snapshot = NetWorthSnapshot(
            date=date.today(),
            total_assets=Decimal("11000.00"),
            total_liabilities=Decimal("0.00"),
            net_worth=Decimal("11000.00"),
            investment_value=Decimal("11000.00"),
            cash_value=Decimal("0.00"),
            account_count=1
        )
        db_session.add(end_snapshot)
        db_session.commit()
        
        handler = QueryHandler(db_session)
        result = handler.handle_query("portfolio performance")
        
        assert result is not None
        assert "performance" in str(result).lower() or "return" in str(result).lower()
    
    def test_handle_holdings_query(self, db_session, test_account):
        """Test holdings query handling"""
        from backend.app.models import Holding
        from datetime import datetime
        
        test_account.type = "investment"
        db_session.commit()
        
        # Add holding
        holding = Holding(
            account_id=test_account.id,
            security_id="sec_1",
            ticker="AAPL",
            name="Apple Inc.",
            quantity=Decimal("10.0"),
            price=Decimal("150.00"),
            value=Decimal("1500.00"),
            cost_basis=Decimal("1400.00"),
            as_of_date=datetime.combine(date.today(), datetime.min.time())
        )
        db_session.add(holding)
        db_session.commit()
        
        handler = QueryHandler(db_session)
        result = handler.handle_query("what stocks do I own")
        
        assert result is not None
        assert "holding" in str(result).lower() or "stock" in str(result).lower()
    
    def test_handle_unknown_query(self, db_session):
        """Test handling of unknown queries"""
        handler = QueryHandler(db_session)
        result = handler.handle_query("random text that doesn't match")
        
        assert result is not None
        assert "unknown" in str(result).lower() or "not understand" in str(result).lower()
    
    def test_handle_query_with_time_range(self, db_session, test_account):
        """Test query with time range"""
        # Add transaction in date range
        txn = Transaction(
            id="txn_1",
            account_id=test_account.id,
            date=date.today() - timedelta(days=5),
            name="Recent Expense",
            amount=Decimal("-30.00"),
            type="expense",
            is_expense=True,
            expense_category="shopping"
        )
        db_session.add(txn)
        db_session.commit()
        
        handler = QueryHandler(db_session)
        result = handler.handle_query("spending this week")
        
        assert result is not None
        assert "expense" in str(result).lower() or "spend" in str(result).lower()
