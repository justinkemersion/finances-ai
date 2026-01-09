"""Net worth snapshot model for daily tracking"""

from sqlalchemy import Column, Numeric, DateTime, Date, Integer, Index, UniqueConstraint
from datetime import datetime, date
from decimal import Decimal
from ..database import Base


class NetWorthSnapshot(Base):
    """Daily snapshot of total net worth"""
    
    __tablename__ = "net_worth_snapshots"
    
    # Primary key - date
    date = Column(Date, primary_key=True, index=True)
    
    # Net worth components
    total_assets = Column(Numeric(precision=20, scale=2), nullable=False, default=Decimal("0"))
    total_liabilities = Column(Numeric(precision=20, scale=2), nullable=False, default=Decimal("0"))
    net_worth = Column(Numeric(precision=20, scale=2), nullable=False, default=Decimal("0"))
    
    # Breakdown by account type (optional, for more detailed tracking)
    investment_value = Column(Numeric(precision=20, scale=2), nullable=True)
    cash_value = Column(Numeric(precision=20, scale=2), nullable=True)
    
    # Metadata
    account_count = Column(Integer, nullable=True)  # Number of accounts included
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Ensure one snapshot per day
    __table_args__ = (
        UniqueConstraint("date", name="uq_net_worth_date"),
        Index("idx_net_worth_date", "date"),
    )
    
    def __repr__(self):
        return f"<NetWorthSnapshot(date={self.date}, net_worth={self.net_worth})>"
