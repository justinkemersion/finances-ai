"""Transaction model for investment transactions"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Boolean, Index, Text, JSON
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
    transaction_datetime = Column(DateTime, nullable=True)  # More precise timestamp from Plaid
    name = Column(String, nullable=False)
    amount = Column(Numeric(precision=20, scale=2), nullable=False)
    currency_code = Column(String, default="USD", nullable=False)
    iso_currency_code = Column(String, nullable=True)  # ISO 4217 currency code
    unofficial_currency_code = Column(String, nullable=True)  # Non-standard currency
    
    # Transaction type
    type = Column(String, nullable=False, index=True)  # e.g., "buy", "sell", "dividend", "fee"
    subtype = Column(String, nullable=True, index=True)  # More specific subtype from Plaid
    category = Column(String, nullable=True, index=True)  # User-defined or Plaid category
    
    # Security information (if applicable)
    security_id = Column(String, nullable=True, index=True)
    ticker = Column(String, nullable=True, index=True)
    quantity = Column(Numeric(precision=20, scale=8), nullable=True)  # Shares
    price = Column(Numeric(precision=20, scale=4), nullable=True)  # Price per share
    fees = Column(Numeric(precision=20, scale=2), nullable=True)  # Transaction fees
    
    # Transaction status and relationships
    is_pending = Column(Boolean, default=False, index=True)
    cancel_transaction_id = Column(String, nullable=True)  # If this transaction was cancelled
    is_cancelled = Column(Boolean, default=False, index=True)  # Whether this transaction is cancelled
    
    # Merchant/location information
    merchant_name = Column(String, nullable=True, index=True)
    location_city = Column(String, nullable=True)
    location_region = Column(String, nullable=True)  # State/province
    location_country = Column(String, nullable=True)
    location_address = Column(String, nullable=True)
    location_postal_code = Column(String, nullable=True)
    
    # Income and deposit classification
    is_income = Column(Boolean, default=False, index=True)  # Is this an income transaction?
    is_deposit = Column(Boolean, default=False, index=True)  # Is this a deposit?
    income_type = Column(String, nullable=True, index=True)  # Type of income (salary, dividend, interest, etc.)
    is_paystub = Column(Boolean, default=False, index=True)  # Is this a payroll/paystub transaction?
    paystub_period_start = Column(DateTime, nullable=True)  # Pay period start date
    paystub_period_end = Column(DateTime, nullable=True)  # Pay period end date
    
    # User-defined categorization and analysis
    user_category = Column(String, nullable=True, index=True)  # User-assigned category
    tags = Column(JSON, nullable=True)  # Array of tags for flexible categorization
    notes = Column(Text, nullable=True)  # User notes about the transaction
    is_tax_deductible = Column(Boolean, nullable=True)  # For tax planning
    tax_category = Column(String, nullable=True)  # Tax category (e.g., "dividend", "capital_gain")
    
    # Analysis and insights
    is_recurring = Column(Boolean, default=False, index=True)  # Detected recurring transaction
    recurring_pattern = Column(String, nullable=True)  # e.g., "monthly", "quarterly"
    confidence_score = Column(Numeric(precision=5, scale=2), nullable=True)  # ML/analysis confidence
    
    # Raw Plaid data (JSON stored for audit/debugging and future extraction)
    plaid_data = Column(JSON, nullable=True)  # Full raw transaction data from Plaid
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    account = relationship("Account", back_populates="transactions")
    
    # Indexes for common queries
    __table_args__ = (
        Index("idx_transaction_account_date", "account_id", "date"),
        Index("idx_transaction_type", "type"),
        Index("idx_transaction_subtype", "subtype"),
        Index("idx_transaction_category", "category"),
        Index("idx_transaction_user_category", "user_category"),
        Index("idx_transaction_security", "security_id"),
        Index("idx_transaction_ticker", "ticker"),
        Index("idx_transaction_merchant", "merchant_name"),
        Index("idx_transaction_pending", "is_pending"),
        Index("idx_transaction_recurring", "is_recurring"),
        Index("idx_transaction_date_range", "date", "account_id"),  # For date range queries
        Index("idx_transaction_income", "is_income"),
        Index("idx_transaction_deposit", "is_deposit"),
        Index("idx_transaction_income_type", "income_type"),
        Index("idx_transaction_paystub", "is_paystub"),
    )
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, account={self.account_id}, type={self.type}, amount={self.amount})>"
