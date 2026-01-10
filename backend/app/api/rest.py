"""REST API interface for Finance AI Analyzer"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from ..database import get_db
from ..queries import QueryHandler
from ..analytics import NetWorthAnalyzer, PerformanceAnalyzer, AllocationAnalyzer
from ..providers import ProviderFactory, ProviderType
from ..models import Account

app = FastAPI(
    title="Finance AI Analyzer API",
    description="Privacy-first personal finance analyzer",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class QueryRequest(BaseModel):
    query: str


class SyncRequest(BaseModel):
    access_token: str
    item_id: str
    provider: Optional[str] = None  # plaid, teller. Defaults to config.DEFAULT_PROVIDER
    sync_holdings: bool = True
    sync_transactions: bool = True


@app.get("/")
def root():
    """API root"""
    return {
        "name": "Finance AI Analyzer API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/query")
def query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Handle a natural language query
    
    Example: {"query": "What's my net worth?"}
    """
    handler = QueryHandler(db)
    result = handler.handle_query(request.query)
    return result


@app.get("/net-worth")
def get_net_worth(
    as_of_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get current net worth"""
    date_obj = None
    if as_of_date:
        date_obj = date.fromisoformat(as_of_date)
    
    net_worth = NetWorthAnalyzer.calculate_current_net_worth(db, as_of_date=date_obj)
    return net_worth


@app.get("/net-worth/history")
def get_net_worth_history(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get net worth history"""
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    
    history = NetWorthAnalyzer.get_net_worth_history(db, start_date=start, end_date=end)
    return {"history": history}


@app.get("/performance")
def get_performance(
    start_date: str,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get portfolio performance"""
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date) if end_date else date.today()
    
    performance = PerformanceAnalyzer.calculate_performance(db, start_date=start, end_date=end)
    return performance


@app.get("/allocation")
def get_allocation(
    account_id: Optional[str] = None,
    as_of_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get portfolio allocation"""
    date_obj = date.fromisoformat(as_of_date) if as_of_date else None
    
    allocation = AllocationAnalyzer.calculate_allocation(
        db,
        account_id=account_id,
        as_of_date=date_obj
    )
    return allocation


@app.get("/holdings")
def get_holdings(
    account_id: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top holdings"""
    holdings = AllocationAnalyzer.get_top_holdings(
        db,
        limit=limit,
        account_id=account_id
    )
    return {"holdings": holdings}


@app.get("/accounts")
def get_accounts(db: Session = Depends(get_db)):
    """List all accounts"""
    accounts = db.query(Account).filter(Account.is_active == True).all()
    return {
        "accounts": [
            {
                "id": acc.id,
                "name": acc.name,
                "type": acc.type,
                "subtype": acc.subtype,
            }
            for acc in accounts
        ]
    }


@app.post("/sync")
def sync(request: SyncRequest, db: Session = Depends(get_db)):
    """Sync data from financial provider (Plaid or Teller)"""
    try:
        from ..config import config
        
        # Determine provider
        provider_type = None
        if request.provider:
            provider_type = ProviderFactory.from_string(request.provider)
        else:
            provider_type = ProviderFactory.from_string(config.DEFAULT_PROVIDER)
        
        sync_handler = ProviderFactory.create_sync(provider_type)
        results = sync_handler.sync_all(
            db=db,
            access_token=request.access_token,
            item_id=request.item_id,
            sync_holdings=request.sync_holdings,
            sync_transactions=request.sync_transactions
        )
        return {
            "status": "success",
            "provider": provider_type.value,
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
