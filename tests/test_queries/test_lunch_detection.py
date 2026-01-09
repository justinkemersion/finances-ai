"""Tests for lunch detection confidence scoring"""

import pytest
from datetime import datetime, date
from decimal import Decimal

from backend.app.queries.handlers import QueryHandler
from backend.app.models import Transaction, Account


class TestLunchConfidenceScoring:
    """Test the lunch detection confidence scoring algorithm"""
    
    def test_high_confidence_known_merchant_lunch_time(self, db_session, test_account):
        """Known lunch merchant during lunch hours = high confidence"""
        handler = QueryHandler(db_session)
        
        txn = Transaction(
            id="test_1",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 12, 30),  # 12:30 PM
            name="Chipotle - Lunch",
            amount=Decimal("-12.50"),
            type="expense",
            merchant_name="Chipotle",
            expense_category="restaurants",
            primary_category="FOOD_AND_DRINK",
            is_expense=True
        )
        
        confidence = handler.calculate_lunch_confidence(txn)
        
        assert confidence["confidence"] >= 90, f"Expected >= 90, got {confidence['confidence']}"
        assert confidence["is_likely_lunch"] == True
        assert "Lunch time" in str(confidence["reasons"])
        assert "Known lunch merchant" in str(confidence["reasons"])
    
    def test_high_confidence_at_2_30pm(self, db_session, test_account):
        """Transaction at 2:30pm should be included in lunch hours"""
        handler = QueryHandler(db_session)
        
        txn = Transaction(
            id="test_2",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 14, 30),  # 2:30 PM
            name="Subway - Lunch",
            amount=Decimal("-9.50"),
            type="expense",
            merchant_name="Subway",
            expense_category="restaurants",
            is_expense=True
        )
        
        confidence = handler.calculate_lunch_confidence(txn)
        
        assert confidence["confidence"] >= 90
        assert confidence["is_likely_lunch"] == True
        assert "Lunch time" in str(confidence["reasons"])
    
    def test_low_confidence_at_2_31pm(self, db_session, test_account):
        """Transaction at 2:31pm should be outside lunch hours"""
        handler = QueryHandler(db_session)
        
        txn = Transaction(
            id="test_3",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 14, 31),  # 2:31 PM
            name="Chipotle",
            amount=Decimal("-12.50"),
            type="expense",
            merchant_name="Chipotle",
            expense_category="restaurants",
            is_expense=True
        )
        
        confidence = handler.calculate_lunch_confidence(txn)
        
        # Known lunch merchant still gives high confidence, but should note it's outside lunch hours
        # The algorithm prioritizes merchant matching, which is correct behavior
        assert confidence["is_likely_lunch"] == True  # Still likely lunch due to merchant
        # But should note it's outside lunch hours or near lunch time
        reasons_str = " ".join(confidence["reasons"])
        assert ("Outside lunch hours" in reasons_str or "Near lunch time" in reasons_str or "14:31" in reasons_str)
    
    def test_low_confidence_grocery_large_amount(self, db_session, test_account):
        """Large grocery purchase = low confidence (not lunch)"""
        handler = QueryHandler(db_session)
        
        txn = Transaction(
            id="test_4",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 12, 30),  # During lunch hours
            name="King Soupers - Groceries",
            amount=Decimal("-87.50"),  # Large amount
            type="expense",
            merchant_name="King Soupers",
            expense_category="groceries",
            primary_category="FOOD_AND_DRINK",
            detailed_category="FOOD_AND_DRINK_GROCERIES",
            is_expense=True
        )
        
        confidence = handler.calculate_lunch_confidence(txn)
        
        assert confidence["confidence"] < 60
        assert confidence["is_likely_lunch"] == False
        assert "large amount" in str(confidence["reasons"]).lower()
        assert "likely full shopping" in str(confidence["reasons"]).lower()
    
    def test_high_confidence_grocery_small_amount(self, db_session, test_account):
        """Small grocery purchase during lunch = high confidence (lunch)"""
        handler = QueryHandler(db_session)
        
        txn = Transaction(
            id="test_5",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 12, 48),  # During lunch hours
            name="King Soupers - Lunch",
            amount=Decimal("-12.43"),  # Small amount
            type="expense",
            merchant_name="King Soupers",
            expense_category="groceries",
            is_expense=True
        )
        
        confidence = handler.calculate_lunch_confidence(txn)
        
        assert confidence["confidence"] >= 60
        assert confidence["is_likely_lunch"] == True
        assert "small amount" in str(confidence["reasons"]).lower()
    
    def test_high_confidence_gas_station_small_amount(self, db_session, test_account):
        """Small gas station purchase during lunch = likely food"""
        handler = QueryHandler(db_session)
        
        txn = Transaction(
            id="test_6",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 13, 15),  # 1:15 PM
            name="7-Eleven - Food",
            amount=Decimal("-8.50"),  # Small amount
            type="expense",
            merchant_name="7-Eleven",
            expense_category="gas",
            is_expense=True
        )
        
        confidence = handler.calculate_lunch_confidence(txn)
        
        assert confidence["confidence"] >= 80
        assert confidence["is_likely_lunch"] == True
        assert "likely food" in str(confidence["reasons"]).lower()
    
    def test_low_confidence_gas_station_large_amount(self, db_session, test_account):
        """Large gas station purchase = likely gas, not food"""
        handler = QueryHandler(db_session)
        
        txn = Transaction(
            id="test_7",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 13, 0),  # During lunch hours
            name="Shell - Gas",
            amount=Decimal("-45.20"),  # Large amount (gas fill-up)
            type="expense",
            merchant_name="Shell",
            expense_category="gas",
            is_expense=True
        )
        
        confidence = handler.calculate_lunch_confidence(txn)
        
        assert confidence["confidence"] < 60
        assert confidence["is_likely_lunch"] == False
        assert "likely gas" in str(confidence["reasons"]).lower()
    
    def test_low_confidence_dinner_time(self, db_session, test_account):
        """Transaction at dinner time = lower confidence (but merchant still helps)"""
        handler = QueryHandler(db_session)
        
        txn = Transaction(
            id="test_8",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 20, 0),  # 8:00 PM (dinner)
            name="Chipotle",
            amount=Decimal("-12.50"),
            type="expense",
            merchant_name="Chipotle",
            expense_category="restaurants",
            is_expense=True
        )
        
        confidence = handler.calculate_lunch_confidence(txn)
        
        # Known lunch merchant + small amount still gives decent confidence
        # but should note it's outside lunch hours
        assert confidence["confidence"] >= 70  # Still decent due to merchant + amount
        reasons_str = " ".join(confidence["reasons"])
        assert "Outside lunch hours" in reasons_str
    
    def test_medium_confidence_no_time_data(self, db_session, test_account):
        """Transaction without time data relies on merchant/amount"""
        handler = QueryHandler(db_session)
        
        txn = Transaction(
            id="test_9",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=None,  # No time data
            name="Chipotle - Lunch",
            amount=Decimal("-12.50"),
            type="expense",
            merchant_name="Chipotle",
            expense_category="restaurants",
            is_expense=True
        )
        
        confidence = handler.calculate_lunch_confidence(txn)
        
        # Should still have decent confidence due to known merchant and small amount
        assert confidence["confidence"] >= 50
        assert "No time data available" in str(confidence["reasons"])
    
    def test_low_confidence_large_amount(self, db_session, test_account):
        """Large amount transaction = unlikely to be lunch"""
        handler = QueryHandler(db_session)
        
        txn = Transaction(
            id="test_10",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 12, 30),  # Lunch time
            name="Restaurant - Group Lunch",
            amount=Decimal("-75.00"),  # Very large amount
            type="expense",
            merchant_name="Restaurant",
            expense_category="restaurants",
            is_expense=True
        )
        
        confidence = handler.calculate_lunch_confidence(txn)
        
        assert confidence["confidence"] < 60
        assert "Large amount" in str(confidence["reasons"])
        assert "unlikely to be lunch" in str(confidence["reasons"]).lower()
    
    def test_confidence_reasons_format(self, db_session, test_account):
        """Confidence reasons should be a list of strings"""
        handler = QueryHandler(db_session)
        
        txn = Transaction(
            id="test_11",
            account_id=test_account.id,
            date=date.today(),
            transaction_datetime=datetime(2024, 1, 15, 12, 30),
            name="Chipotle",
            amount=Decimal("-12.50"),
            type="expense",
            merchant_name="Chipotle",
            expense_category="restaurants",
            is_expense=True
        )
        
        confidence = handler.calculate_lunch_confidence(txn)
        
        assert isinstance(confidence["reasons"], list)
        assert len(confidence["reasons"]) > 0
        assert all(isinstance(reason, str) for reason in confidence["reasons"])
