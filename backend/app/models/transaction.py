"""Transaction model for investment transactions"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from ..database import Base


class Transaction(Base):
    """Represents an investment transaction"""
    
    __tablename__ = "transactions"
    
    # Primary key - Plaid transaction_id
    id = Column(String, primary_key=True, index=True)
    
    # Foreign key to account
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False, index=True)
    
    # Transaction details
    date = Column(DateTime, nullable=False, index=True)
    name = Column(String, nullable=False)
    amount = Column(Numeric(precision=20, scale=2), nullable=False)
    currency_code = Column(String, default="USD", nullable=False)
    
    # Transaction type
    type = Column(String, nullable=False)  # e.g., "buy", "sell", "dividend", "fee"
    category = Column(String, nullable=True)  # More specific category
    
    # Security information (if applicable)
    security_id = Column(String, nullable=True, index=True)
    ticker = Column(String, nullable=True, index=True)
    quantity = Column(Numeric(precision=20, scale=8), nullable=True)  # Shares
    price = Column(Numeric(precision=20, scale=4), nullable=True)  # Price per share
    
    # Additional metadata
    is_pending = Column(Boolean, default=False)
    merchant_name = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    account = relationship("Account", back_populates="transactions")
    
    # Indexes
    __table_args__ = (
        Index("idx_transaction_account_date", "account_id", "date"),
        Index("idx_transaction_type", "type"),
        Index("idx_transaction_security", "security_id"),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, account={self.account_id}, type={self.type}, amount={self.amount})>"
