"""Holding model for investment holdings"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from ..database import Base


class Holding(Base):
    """Represents an investment holding (stock, bond, etc.)"""
    
    __tablename__ = "holdings"
    
    # Composite primary key: account_id + security_id
    account_id = Column(String, ForeignKey("accounts.id"), primary_key=True)
    security_id = Column(String, primary_key=True)  # Plaid security_id
    
    # Security information
    name = Column(String, nullable=False)
    ticker = Column(String, nullable=True, index=True)
    cusip = Column(String, nullable=True)
    isin = Column(String, nullable=True)
    sedol = Column(String, nullable=True)
    security_type = Column(String, nullable=True)  # e.g., "equity", "etf", "mutual fund"
    
    # Holding quantities and values
    quantity = Column(Numeric(precision=20, scale=8), nullable=False, default=Decimal("0"))
    price = Column(Numeric(precision=20, scale=4), nullable=True)  # Current price
    value = Column(Numeric(precision=20, scale=2), nullable=False, default=Decimal("0"))  # Total value
    
    # Cost basis information
    cost_basis = Column(Numeric(precision=20, scale=2), nullable=True)
    cost_basis_per_share = Column(Numeric(precision=20, scale=4), nullable=True)
    
    # Timestamps
    as_of_date = Column(DateTime, nullable=False, index=True)  # When this holding snapshot was taken
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    account = relationship("Account", back_populates="holdings")
    
    # Indexes
    __table_args__ = (
        Index("idx_holding_account_date", "account_id", "as_of_date"),
        Index("idx_holding_ticker", "ticker"),
        Index("idx_holding_security_type", "security_type"),
    )
    
    def __repr__(self):
        return f"<Holding(account={self.account_id}, ticker={self.ticker}, quantity={self.quantity})>"
