"""Pytest configuration and fixtures"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
from decimal import Decimal

from backend.app.database import Base
from backend.app.models import Account, Transaction


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def test_account(db_session):
    """Create a test account"""
    account = Account(
        id="test_account_123",
        item_id="test_item",
        name="Test Checking Account",
        type="depository",
        subtype="checking",
        institution_id="test_institution",
        is_active=True
    )
    db_session.add(account)
    db_session.commit()
    return account


@pytest.fixture
def sample_transaction(db_session, test_account):
    """Create a sample transaction"""
    txn = Transaction(
        id="test_txn_123",
        account_id=test_account.id,
        date=date.today(),
        transaction_datetime=datetime(2024, 1, 15, 12, 30),  # 12:30 PM
        name="Chipotle - Lunch",
        amount=Decimal("-12.50"),
        currency_code="USD",
        iso_currency_code="USD",
        type="expense",
        merchant_name="Chipotle",
        expense_category="restaurants",
        primary_category="FOOD_AND_DRINK",
        detailed_category="FOOD_AND_DRINK_RESTAURANTS",
        is_expense=True,
        is_pending=False
    )
    db_session.add(txn)
    db_session.commit()
    return txn
