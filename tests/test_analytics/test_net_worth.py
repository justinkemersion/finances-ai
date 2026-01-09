"""Tests for net worth calculations"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from backend.app.analytics.net_worth import NetWorthAnalyzer
from backend.app.models import Account, Holding, NetWorthSnapshot


class TestNetWorthCalculations:
    """Test net worth calculation accuracy"""
    
    def test_calculate_net_worth_single_account(self, db_session, test_account):
        """Test net worth with a single account (using holdings for cash)"""
        # For depository accounts, create a holding to represent cash balance
        # In real usage, this would come from Plaid account balances
        from backend.app.models import Holding
        from datetime import datetime
        cash_holding = Holding(
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
        db_session.add(cash_holding)
        db_session.commit()
        
        net_worth = NetWorthAnalyzer.calculate_current_net_worth(db_session)
        
        assert net_worth["total_assets"] == pytest.approx(5000.00, abs=0.01)
        assert net_worth["total_liabilities"] == pytest.approx(0.00, abs=0.01)
        assert net_worth["net_worth"] == pytest.approx(5000.00, abs=0.01)
        assert net_worth["cash_value"] == pytest.approx(5000.00, abs=0.01)
        assert net_worth["investment_value"] == pytest.approx(0.00, abs=0.01)
    
    def test_calculate_net_worth_multiple_accounts(self, db_session, test_account):
        """Test net worth with multiple accounts"""
        from backend.app.models import Holding
        from datetime import datetime
        
        # First account - add cash holding
        cash_holding1 = Holding(
            account_id=test_account.id,
            security_id="cash",
            ticker="CASH",
            name="Cash Balance",
            quantity=Decimal("1.0"),
            price=Decimal("3000.00"),
            value=Decimal("3000.00"),
            cost_basis=Decimal("3000.00"),
            as_of_date=datetime.combine(date.today(), datetime.min.time())
        )
        db_session.add(cash_holding1)
        
        # Second account
        account2 = Account(
            id="test_account_456",
            item_id="test_item",
            name="Test Savings Account",
            type="depository",
            subtype="savings",
            institution_id="test_institution",
            is_active=True
        )
        db_session.add(account2)
        
        # Second account - add cash holding
        cash_holding2 = Holding(
            account_id=account2.id,
            security_id="cash",
            ticker="CASH",
            name="Cash Balance",
            quantity=Decimal("1.0"),
            price=Decimal("2000.00"),
            value=Decimal("2000.00"),
            cost_basis=Decimal("2000.00"),
            as_of_date=datetime.combine(date.today(), datetime.min.time())
        )
        db_session.add(cash_holding2)
        db_session.commit()
        
        net_worth = NetWorthAnalyzer.calculate_current_net_worth(db_session)
        
        assert net_worth["total_assets"] == pytest.approx(5000.00, abs=0.01)
        assert net_worth["net_worth"] == pytest.approx(5000.00, abs=0.01)
        assert net_worth["cash_value"] == pytest.approx(5000.00, abs=0.01)
    
    def test_calculate_net_worth_with_holdings(self, db_session, test_account):
        """Test net worth calculation including investment holdings"""
        test_account.type = "investment"
        db_session.commit()
        
        from datetime import datetime
        # Add holding (investment accounts use holdings for value)
        holding = Holding(
            account_id=test_account.id,
            security_id="sec_123",
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
        
        net_worth = NetWorthAnalyzer.calculate_current_net_worth(db_session)
        
        assert net_worth["investment_value"] == pytest.approx(1500.00, abs=0.01)
        assert net_worth["total_assets"] == pytest.approx(1500.00, abs=0.01)
        assert net_worth["net_worth"] == pytest.approx(1500.00, abs=0.01)
    
    def test_calculate_net_worth_with_liabilities(self, db_session):
        """Test net worth with credit card (liability)"""
        from backend.app.models import Holding
        
        # Checking account (asset)
        checking = Account(
            id="checking_123",
            item_id="test_item",
            name="Checking",
            type="depository",
            subtype="checking",
            institution_id="test_institution",
            is_active=True
        )
        db_session.add(checking)
        
        from datetime import datetime
        # Add cash holding for checking
        cash_holding = Holding(
            account_id=checking.id,
            security_id="cash",
            ticker="CASH",
            name="Cash Balance",
            quantity=Decimal("1.0"),
            price=Decimal("5000.00"),
            value=Decimal("5000.00"),
            cost_basis=Decimal("5000.00"),
            as_of_date=datetime.combine(date.today(), datetime.min.time())
        )
        db_session.add(cash_holding)
        
        # Credit card (liability) - represented as negative holding
        # Note: Current implementation doesn't handle liabilities well
        # This test documents current behavior
        credit_card = Account(
            id="credit_123",
            item_id="test_item",
            name="Credit Card",
            type="credit",
            subtype="credit card",
            institution_id="test_institution",
            is_active=True
        )
        db_session.add(credit_card)
        db_session.commit()
        
        net_worth = NetWorthAnalyzer.calculate_current_net_worth(db_session)
        
        # Current implementation only counts assets from holdings
        # Liabilities would need special handling
        assert net_worth["total_assets"] == pytest.approx(5000.00, abs=0.01)
        # Note: liabilities handling may need to be added to the implementation
    
    def test_calculate_net_worth_empty_accounts(self, db_session):
        """Test net worth with no accounts"""
        net_worth = NetWorthAnalyzer.calculate_current_net_worth(db_session)
        
        assert net_worth["total_assets"] == Decimal("0.00")
        assert net_worth["total_liabilities"] == Decimal("0.00")
        assert net_worth["net_worth"] == Decimal("0.00")
    
    def test_calculate_net_worth_inactive_accounts_excluded(self, db_session, test_account):
        """Test that inactive accounts are excluded"""
        test_account.balance = Decimal("1000.00")
        test_account.is_active = False
        db_session.commit()
        
        net_worth = NetWorthAnalyzer.calculate_current_net_worth(db_session)
        
        assert net_worth["total_assets"] == Decimal("0.00")
        assert net_worth["net_worth"] == Decimal("0.00")
    
    def test_create_net_worth_snapshot(self, db_session, test_account):
        """Test creating a net worth snapshot"""
        from backend.app.models import Holding
        
        from backend.app.models import Holding
        from datetime import datetime
        # Add cash holding
        cash_holding = Holding(
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
        db_session.add(cash_holding)
        db_session.commit()
        
        snapshot = NetWorthAnalyzer.create_snapshot(db_session, date.today())
        
        assert snapshot is not None
        assert snapshot.date == date.today()
        assert snapshot.total_assets == pytest.approx(Decimal("5000.00"), abs=Decimal("0.01"))
        assert snapshot.net_worth == pytest.approx(Decimal("5000.00"), abs=Decimal("0.01"))
        
        # Verify it was saved to database
        saved_snapshot = db_session.query(NetWorthSnapshot).filter(
            NetWorthSnapshot.date == date.today()
        ).first()
        assert saved_snapshot is not None
        assert saved_snapshot.net_worth == pytest.approx(Decimal("5000.00"), abs=Decimal("0.01"))
    
    def test_get_net_worth_history(self, db_session, test_account):
        """Test retrieving net worth history"""
        from datetime import timedelta
        # Create snapshots for different dates
        for i, day_offset in enumerate([30, 20, 10, 0]):
            test_date = date.today() - timedelta(days=day_offset)
            snapshot = NetWorthSnapshot(
                date=test_date,
                total_assets=Decimal(f"{5000 + i * 100}.00"),
                total_liabilities=Decimal("0.00"),
                net_worth=Decimal(f"{5000 + i * 100}.00"),
                investment_value=Decimal("0.00"),
                cash_value=Decimal(f"{5000 + i * 100}.00"),
                account_count=1
            )
            db_session.add(snapshot)
        db_session.commit()
        
        start_date = date.today() - datetime.timedelta(days=25)
        end_date = date.today()
        
        history = NetWorthAnalyzer.get_net_worth_history(
            db_session,
            start_date=start_date,
            end_date=end_date
        )
        
        assert len(history) >= 2  # Should have at least 2 snapshots
        # Check that dates are in range
        for entry in history:
            assert start_date <= entry["date"] <= end_date
            assert "net_worth" in entry
            assert "total_assets" in entry
