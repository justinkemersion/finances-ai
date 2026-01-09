"""Query handlers for different intents"""

from typing import Dict, Any, Optional
from datetime import date
from sqlalchemy.orm import Session

from .intent_router import QueryIntent, IntentRouter
from ..analytics import NetWorthAnalyzer, PerformanceAnalyzer, AllocationAnalyzer
from ..models import Account, Transaction


class QueryHandler:
    """Handles queries and routes to appropriate analytics"""
    
    def __init__(self, db: Session):
        """
        Initialize query handler
        
        Args:
            db: Database session
        """
        self.db = db
    
    def handle_query(self, query: str) -> Dict[str, Any]:
        """
        Handle a natural language query
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary with query results
        """
        parsed = IntentRouter.parse_query(query)
        intent = parsed["intent"]
        
        if intent == QueryIntent.NET_WORTH:
            return self.handle_net_worth(parsed)
        elif intent == QueryIntent.PERFORMANCE:
            return self.handle_performance(parsed)
        elif intent == QueryIntent.ALLOCATION:
            return self.handle_allocation(parsed)
        elif intent == QueryIntent.HOLDINGS:
            return self.handle_holdings(parsed)
        elif intent == QueryIntent.TRANSACTIONS:
            return self.handle_transactions(parsed)
        else:
            return {
                "error": "Could not understand query",
                "query": query,
                "suggestions": [
                    "What's my net worth?",
                    "How did my portfolio perform last month?",
                    "What's my allocation?",
                    "Show my holdings",
                    "Show recent transactions",
                ]
            }
    
    def handle_net_worth(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle net worth queries"""
        time_range = parsed.get("time_range")
        as_of_date = time_range[1] if time_range else None
        
        if time_range and time_range[0] != time_range[1]:
            # Range query - get history
            history = NetWorthAnalyzer.get_net_worth_history(
                self.db,
                start_date=time_range[0],
                end_date=time_range[1]
            )
            return {
                "intent": "net_worth",
                "type": "history",
                "data": history,
            }
        else:
            # Current net worth
            net_worth = NetWorthAnalyzer.calculate_current_net_worth(
                self.db,
                as_of_date=as_of_date
            )
            return {
                "intent": "net_worth",
                "type": "current",
                "data": net_worth,
            }
    
    def handle_performance(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle performance queries"""
        time_range = parsed.get("time_range")
        
        if not time_range:
            # Default to last month
            from datetime import timedelta
            time_range = (date.today() - timedelta(days=30), date.today())
        
        performance = PerformanceAnalyzer.calculate_performance(
            self.db,
            start_date=time_range[0],
            end_date=time_range[1]
        )
        
        # Also get monthly breakdown if range is long enough
        if (time_range[1] - time_range[0]).days > 60:
            monthly = PerformanceAnalyzer.get_monthly_performance(
                self.db,
                months=max(1, (time_range[1] - time_range[0]).days // 30)
            )
            performance["monthly_breakdown"] = monthly
        
        return {
            "intent": "performance",
            "data": performance,
        }
    
    def handle_allocation(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle allocation queries"""
        account_filter = parsed.get("account_filter")
        account_id = None
        
        if account_filter:
            # Try to find account by name or ID
            account = self.db.query(Account).filter(
                (Account.name.ilike(f"%{account_filter}%")) |
                (Account.id == account_filter)
            ).first()
            if account:
                account_id = account.id
        
        allocation = AllocationAnalyzer.calculate_allocation(
            self.db,
            account_id=account_id
        )
        
        return {
            "intent": "allocation",
            "data": allocation,
        }
    
    def handle_holdings(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle holdings queries"""
        account_filter = parsed.get("account_filter")
        account_id = None
        
        if account_filter:
            account = self.db.query(Account).filter(
                (Account.name.ilike(f"%{account_filter}%")) |
                (Account.id == account_filter)
            ).first()
            if account:
                account_id = account.id
        
        # Get top holdings
        holdings = AllocationAnalyzer.get_top_holdings(
            self.db,
            limit=20,
            account_id=account_id
        )
        
        return {
            "intent": "holdings",
            "data": {
                "holdings": holdings,
                "count": len(holdings),
            }
        }
    
    def handle_transactions(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle transaction queries"""
        time_range = parsed.get("time_range")
        account_filter = parsed.get("account_filter")
        
        if not time_range:
            from datetime import timedelta
            time_range = (date.today() - timedelta(days=30), date.today())
        
        query = self.db.query(Transaction).filter(
            Transaction.date >= time_range[0],
            Transaction.date <= time_range[1]
        )
        
        if account_filter:
            account = self.db.query(Account).filter(
                (Account.name.ilike(f"%{account_filter}%")) |
                (Account.id == account_filter)
            ).first()
            if account:
                query = query.filter(Transaction.account_id == account.id)
        
        transactions = query.order_by(Transaction.date.desc()).limit(50).all()
        
        return {
            "intent": "transactions",
            "data": {
                "transactions": [
                    {
                        "id": txn.id,
                        "date": txn.date.isoformat(),
                        "name": txn.name,
                        "type": txn.type,
                        "amount": float(txn.amount),
                        "ticker": txn.ticker,
                        "quantity": float(txn.quantity) if txn.quantity else None,
                    }
                    for txn in transactions
                ],
                "count": len(transactions),
            }
        }
