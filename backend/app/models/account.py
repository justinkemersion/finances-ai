"""Account model for financial accounts"""

from sqlalchemy import Column, String, DateTime, Boolean, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base


class Account(Base):
    """Represents a financial account from Plaid"""
    
    __tablename__ = "accounts"
    
    # Primary key - Plaid account_id
    id = Column(String, primary_key=True, index=True)
    
    # Plaid item_id (the institution connection)
    item_id = Column(String, nullable=False, index=True)
    
    # Account metadata
    name = Column(String, nullable=False)
    official_name = Column(String, nullable=True)
    type = Column(String, nullable=False)  # e.g., "investment", "depository"
    subtype = Column(String, nullable=True)  # e.g., "brokerage", "401k"
    
    # Institution info
    institution_id = Column(String, nullable=True)
    institution_name = Column(String, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    mask = Column(String, nullable=True)  # Last 4 digits or account mask
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Raw Plaid data (JSON stored as text for audit/debugging)
    plaid_data = Column(Text, nullable=True)
    
    # Relationships
    holdings = relationship("Holding", back_populates="account", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_account_item_id", "item_id"),
        Index("idx_account_type", "type"),
    )
    
    def __repr__(self):
        return f"<Account(id={self.id}, name={self.name}, type={self.type})>"
