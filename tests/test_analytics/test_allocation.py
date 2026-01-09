"""Tests for portfolio allocation calculations"""

import pytest
from datetime import date
from decimal import Decimal

from backend.app.analytics.allocation import AllocationAnalyzer
from backend.app.models import Account, Holding


class TestAllocationCalculations:
    """Test portfolio allocation calculation accuracy"""
    
    def test_calculate_allocation_single_holding(self, db_session, test_account):
        """Test allocation with a single holding"""
        test_account.type = "investment"
        db_session.commit()
        
        from datetime import datetime
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
        
        allocation = AllocationAnalyzer.calculate_allocation(db_session)
        
        assert allocation["total_value"] == Decimal("1500.00")
        assert len(allocation["by_security"]) == 1
        assert allocation["by_security"][0]["ticker"] == "AAPL"
        assert allocation["by_security"][0]["allocation_percent"] == Decimal("100.00")
    
    def test_calculate_allocation_multiple_holdings(self, db_session, test_account):
        """Test allocation with multiple holdings"""
        test_account.type = "investment"
        db_session.commit()
        
        holdings = [
            ("AAPL", Decimal("1500.00")),
            ("MSFT", Decimal("1000.00")),
            ("GOOGL", Decimal("500.00")),
        ]
        
        from datetime import datetime
        for i, (ticker, value) in enumerate(holdings):
            holding = Holding(
                account_id=test_account.id,
                security_id=f"sec_{i}",
                ticker=ticker,
                name=f"{ticker} Inc.",
                quantity=Decimal("10.0"),
                price=Decimal(str(value / 10)),
                value=value,
                cost_basis=value - Decimal("100.00"),
                as_of_date=datetime.combine(date.today(), datetime.min.time())
            )
            db_session.add(holding)
        db_session.commit()
        
        allocation = AllocationAnalyzer.calculate_allocation(db_session)
        
        total = Decimal("3000.00")
        assert allocation["total_value"] == total
        
        # Check allocations sum to 100%
        total_percent = sum(
            Decimal(str(h["allocation_percent"])) 
            for h in allocation["by_security"]
        )
        assert abs(total_percent - Decimal("100.00")) < Decimal("0.01")  # Allow small rounding
        
        # Check individual allocations
        aapl = next(h for h in allocation["by_security"] if h["ticker"] == "AAPL")
        assert aapl["allocation_percent"] == Decimal("50.00")  # 1500/3000 = 50%
        
        msft = next(h for h in allocation["by_security"] if h["ticker"] == "MSFT")
        assert msft["allocation_percent"] == pytest.approx(33.33, abs=0.1)  # 1000/3000 ≈ 33.33%
    
    def test_calculate_allocation_empty_portfolio(self, db_session):
        """Test allocation with no holdings"""
        allocation = AllocationAnalyzer.calculate_allocation(db_session)
        
        assert allocation["total_value"] == Decimal("0.00")
        assert len(allocation["by_security"]) == 0
    
    def test_calculate_allocation_by_account(self, db_session):
        """Test allocation filtered by account"""
        # Account 1
        account1 = Account(
            id="account_1",
            item_id="test_item",
            name="IRA Account",
            type="investment",
            subtype="ira",
            institution_id="test_institution",
            is_active=True
        )
        db_session.add(account1)
        
        # Account 2
        account2 = Account(
            id="account_2",
            item_id="test_item",
            name="Brokerage Account",
            type="investment",
            subtype="brokerage",
            institution_id="test_institution",
            is_active=True
        )
        db_session.add(account2)
        db_session.commit()
        
        from datetime import datetime
        # Holdings in account 1
        holding1 = Holding(
            account_id=account1.id,
            security_id="sec_1",
            ticker="AAPL",
            name="Apple",
            quantity=Decimal("10.0"),
            price=Decimal("150.00"),
            value=Decimal("1500.00"),
            cost_basis=Decimal("1400.00"),
            as_of_date=datetime.combine(date.today(), datetime.min.time())
        )
        db_session.add(holding1)
        
        # Holdings in account 2
        holding2 = Holding(
            account_id=account2.id,
            security_id="sec_2",
            ticker="MSFT",
            name="Microsoft",
            quantity=Decimal("10.0"),
            price=Decimal("200.00"),
            value=Decimal("2000.00"),
            cost_basis=Decimal("1900.00"),
            as_of_date=datetime.combine(date.today(), datetime.min.time())
        )
        db_session.add(holding2)
        db_session.commit()
        
        # Get allocation for account 1 only
        allocation = AllocationAnalyzer.calculate_allocation(
            db_session,
            account_id=account1.id
        )
        
        assert allocation["total_value"] == Decimal("1500.00")
        assert len(allocation["by_security"]) == 1
        assert allocation["by_security"][0]["ticker"] == "AAPL"
    
    def test_get_top_holdings(self, db_session, test_account):
        """Test getting top holdings"""
        test_account.type = "investment"
        db_session.commit()
        
        # Create multiple holdings
        holdings_data = [
            ("AAPL", Decimal("1500.00")),
            ("MSFT", Decimal("1000.00")),
            ("GOOGL", Decimal("500.00")),
            ("TSLA", Decimal("200.00")),
        ]
        
        from datetime import datetime
        for i, (ticker, value) in enumerate(holdings_data):
            holding = Holding(
                account_id=test_account.id,
                security_id=f"sec_{i}",
                ticker=ticker,
                name=f"{ticker} Inc.",
                quantity=Decimal("10.0"),
                price=Decimal(str(value / 10)),
                value=value,
                cost_basis=value - Decimal("50.00"),
                as_of_date=datetime.combine(date.today(), datetime.min.time())
            )
            db_session.add(holding)
        db_session.commit()
        
        top_holdings = AllocationAnalyzer.get_top_holdings(db_session, limit=3)
        
        assert len(top_holdings) == 3
        # Should be sorted by value descending
        assert top_holdings[0]["ticker"] == "AAPL"
        assert top_holdings[1]["ticker"] == "MSFT"
        assert top_holdings[2]["ticker"] == "GOOGL"
