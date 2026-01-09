"""Tests for portfolio performance calculations"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from backend.app.analytics.performance import PerformanceAnalyzer
from backend.app.models import NetWorthSnapshot


class TestPerformanceCalculations:
    """Test portfolio performance calculation accuracy"""
    
    def test_calculate_performance_positive_return(self, db_session):
        """Test performance calculation with positive return"""
        # Start snapshot
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
        
        # End snapshot
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
        
        start_date = date.today() - timedelta(days=30)
        performance = PerformanceAnalyzer.calculate_performance(
            db_session,
            start_date=start_date
        )
        
        assert performance["start_value"] == Decimal("10000.00")
        assert performance["end_value"] == Decimal("11000.00")
        assert performance["absolute_return"] == Decimal("1000.00")
        assert performance["percent_return"] == Decimal("10.00")  # 10% return
    
    def test_calculate_performance_negative_return(self, db_session):
        """Test performance calculation with negative return"""
        start_snapshot = NetWorthSnapshot(
            date=date.today() - timedelta(days=30),
            total_assets=Decimal("10000.00"),
            net_worth=Decimal("10000.00"),
            investment_value=Decimal("10000.00"),
            cash_value=Decimal("0.00"),
            account_count=1
        )
        db_session.add(start_snapshot)
        
        end_snapshot = NetWorthSnapshot(
            date=date.today(),
            total_assets=Decimal("9000.00"),
            net_worth=Decimal("9000.00"),
            investment_value=Decimal("9000.00"),
            cash_value=Decimal("0.00"),
            account_count=1
        )
        db_session.add(end_snapshot)
        db_session.commit()
        
        start_date = date.today() - timedelta(days=30)
        performance = PerformanceAnalyzer.calculate_performance(
            db_session,
            start_date=start_date
        )
        
        assert performance["absolute_return"] == Decimal("-1000.00")
        assert performance["percent_return"] == Decimal("-10.00")  # -10% return
    
    def test_calculate_performance_zero_return(self, db_session):
        """Test performance calculation with no change"""
        start_snapshot = NetWorthSnapshot(
            date=date.today() - timedelta(days=30),
            total_assets=Decimal("10000.00"),
            net_worth=Decimal("10000.00"),
            investment_value=Decimal("10000.00"),
            cash_value=Decimal("0.00"),
            account_count=1
        )
        db_session.add(start_snapshot)
        
        end_snapshot = NetWorthSnapshot(
            date=date.today(),
            total_assets=Decimal("10000.00"),
            net_worth=Decimal("10000.00"),
            investment_value=Decimal("10000.00"),
            cash_value=Decimal("0.00"),
            account_count=1
        )
        db_session.add(end_snapshot)
        db_session.commit()
        
        start_date = date.today() - timedelta(days=30)
        performance = PerformanceAnalyzer.calculate_performance(
            db_session,
            start_date=start_date
        )
        
        assert performance["absolute_return"] == Decimal("0.00")
        assert performance["percent_return"] == Decimal("0.00")
    
    def test_calculate_performance_annualized(self, db_session):
        """Test annualized return calculation"""
        # 6 months of data with 10% return
        start_snapshot = NetWorthSnapshot(
            date=date.today() - timedelta(days=180),
            total_assets=Decimal("10000.00"),
            net_worth=Decimal("10000.00"),
            investment_value=Decimal("10000.00"),
            cash_value=Decimal("0.00"),
            account_count=1
        )
        db_session.add(start_snapshot)
        
        end_snapshot = NetWorthSnapshot(
            date=date.today(),
            total_assets=Decimal("11000.00"),
            net_worth=Decimal("11000.00"),
            investment_value=Decimal("11000.00"),
            cash_value=Decimal("0.00"),
            account_count=1
        )
        db_session.add(end_snapshot)
        db_session.commit()
        
        start_date = date.today() - timedelta(days=180)
        performance = PerformanceAnalyzer.calculate_performance(
            db_session,
            start_date=start_date
        )
        
        # 10% over 6 months should annualize to ~21% (not exactly 20% due to compounding)
        assert performance["percent_return"] == Decimal("10.00")
        assert "annualized_return" in performance
        # Annualized should be approximately 2x (for 6 months)
        assert float(performance["annualized_return"]) > 19.0
        assert float(performance["annualized_return"]) < 22.0
    
    def test_calculate_performance_creates_missing_snapshots(self, db_session):
        """Test that missing snapshots are created automatically"""
        # No snapshots exist
        start_date = date.today() - timedelta(days=30)
        
        performance = PerformanceAnalyzer.calculate_performance(
            db_session,
            start_date=start_date
        )
        
        # Should have created snapshots
        start_snapshot = db_session.query(NetWorthSnapshot).filter(
            NetWorthSnapshot.date == start_date
        ).first()
        end_snapshot = db_session.query(NetWorthSnapshot).filter(
            NetWorthSnapshot.date == date.today()
        ).first()
        
        assert start_snapshot is not None
        assert end_snapshot is not None
        assert "start_value" in performance
        assert "end_value" in performance
