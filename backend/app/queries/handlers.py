"""Query handlers for different intents"""

from typing import Dict, Any, Optional
from datetime import date
from sqlalchemy.orm import Session

from .intent_router import QueryIntent, IntentRouter
from ..analytics import (
    NetWorthAnalyzer, PerformanceAnalyzer, AllocationAnalyzer,
    IncomeAnalyzer, ExpenseAnalyzer
)
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
        elif intent == QueryIntent.INCOME:
            return self.handle_income(parsed)
        elif intent == QueryIntent.EXPENSES:
            return self.handle_expenses(parsed)
        elif intent == QueryIntent.SPENDING_CATEGORY:
            return self.handle_spending_category(parsed)
        elif intent == QueryIntent.DIVIDENDS:
            return self.handle_dividends(parsed)
        elif intent == QueryIntent.CASH_FLOW:
            return self.handle_cash_flow(parsed)
        elif intent == QueryIntent.MERCHANT:
            return self.handle_merchant(parsed)
        else:
            return {
                "error": "Could not understand query",
                "query": query,
                "suggestions": [
                    "What's my net worth?",
                    "How much did I earn last month?",
                    "How much did I spend on beer?",
                    "Show my expenses",
                    "What are my dividends?",
                    "How's my cash flow?",
                    "How much at Starbucks?",
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
    
    def handle_income(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle income queries"""
        time_range = parsed.get("time_range")
        account_filter = parsed.get("account_filter")
        account_id = None
        
        if account_filter:
            account = self.db.query(Account).filter(
                (Account.name.ilike(f"%{account_filter}%")) |
                (Account.id == account_filter)
            ).first()
            if account:
                account_id = account.id
        
        if time_range:
            income_summary = IncomeAnalyzer.calculate_income_summary(
                self.db,
                start_date=time_range[0],
                end_date=time_range[1],
                account_id=account_id
            )
        else:
            income_summary = IncomeAnalyzer.calculate_income_summary(
                self.db,
                account_id=account_id
            )
        
        return {
            "intent": "income",
            "data": income_summary,
        }
    
    def handle_expenses(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle expense queries"""
        time_range = parsed.get("time_range")
        account_filter = parsed.get("account_filter")
        account_id = None
        
        if account_filter:
            account = self.db.query(Account).filter(
                (Account.name.ilike(f"%{account_filter}%")) |
                (Account.id == account_filter)
            ).first()
            if account:
                account_id = account.id
        
        if time_range:
            expense_summary = ExpenseAnalyzer.calculate_expense_summary(
                self.db,
                start_date=time_range[0],
                end_date=time_range[1],
                account_id=account_id
            )
        else:
            expense_summary = ExpenseAnalyzer.calculate_expense_summary(
                self.db,
                account_id=account_id
            )
        
        return {
            "intent": "expenses",
            "data": expense_summary,
        }
    
    def handle_spending_category(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle category-specific spending queries (e.g., 'how much on beer?')"""
        time_range = parsed.get("time_range")
        category = parsed.get("category")
        account_filter = parsed.get("account_filter")
        amount_threshold = parsed.get("amount_threshold")
        account_id = None
        
        if account_filter:
            account = self.db.query(Account).filter(
                (Account.name.ilike(f"%{account_filter}%")) |
                (Account.id == account_filter)
            ).first()
            if account:
                account_id = account.id
        
        if not time_range:
            from datetime import timedelta
            time_range = (date.today() - timedelta(days=30), date.today())
        
        # Get expenses filtered by category
        query = self.db.query(Transaction).filter(
            Transaction.is_expense == True,
            Transaction.date >= time_range[0],
            Transaction.date <= time_range[1]
        )
        
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        
        if category:
            # Try to match category in expense_category or primary_category
            query = query.filter(
                (Transaction.expense_category.ilike(f"%{category}%")) |
                (Transaction.primary_category.ilike(f"%{category}%")) |
                (Transaction.detailed_category.ilike(f"%{category}%")) |
                (Transaction.merchant_name.ilike(f"%{category}%"))
            )
        
        if amount_threshold:
            query = query.filter(Transaction.amount <= -abs(amount_threshold))
        
        transactions = query.order_by(Transaction.date.desc()).all()
        
        total = sum(abs(float(txn.amount)) for txn in transactions)
        
        return {
            "intent": "spending_category",
            "category": category,
            "data": {
                "total": total,
                "count": len(transactions),
                "transactions": [
                    {
                        "date": txn.date.isoformat(),
                        "name": txn.name,
                        "merchant": txn.merchant_name,
                        "amount": float(abs(txn.amount)),
                        "category": txn.expense_category or txn.primary_category,
                    }
                    for txn in transactions[:20]  # Limit to 20 for display
                ],
            }
        }
    
    def handle_dividends(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle dividend queries"""
        time_range = parsed.get("time_range")
        account_filter = parsed.get("account_filter")
        account_id = None
        
        if account_filter:
            account = self.db.query(Account).filter(
                (Account.name.ilike(f"%{account_filter}%")) |
                (Account.id == account_filter)
            ).first()
            if account:
                account_id = account.id
        
        if not time_range:
            from datetime import timedelta
            time_range = (date.today() - timedelta(days=365), date.today())
        
        # Get dividend transactions
        query = self.db.query(Transaction).filter(
            Transaction.type == "dividend",
            Transaction.date >= time_range[0],
            Transaction.date <= time_range[1]
        )
        
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        
        dividends = query.order_by(Transaction.date.desc()).all()
        
        total = sum(float(txn.amount) for txn in dividends)
        
        return {
            "intent": "dividends",
            "data": {
                "total": total,
                "count": len(dividends),
                "dividends": [
                    {
                        "date": txn.date.isoformat(),
                        "name": txn.name,
                        "ticker": txn.ticker,
                        "amount": float(txn.amount),
                        "quantity": float(txn.quantity) if txn.quantity else None,
                    }
                    for txn in dividends
                ],
            }
        }
    
    def handle_cash_flow(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle cash flow queries (income vs expenses)"""
        time_range = parsed.get("time_range")
        account_filter = parsed.get("account_filter")
        account_id = None
        
        if account_filter:
            account = self.db.query(Account).filter(
                (Account.name.ilike(f"%{account_filter}%")) |
                (Account.id == account_filter)
            ).first()
            if account:
                account_id = account.id
        
        if not time_range:
            from datetime import timedelta
            time_range = (date.today().replace(day=1), date.today())
        
        # Get income summary
        income_summary = IncomeAnalyzer.calculate_income_summary(
            self.db,
            start_date=time_range[0],
            end_date=time_range[1],
            account_id=account_id
        )
        
        # Get expense summary
        expense_summary = ExpenseAnalyzer.calculate_expense_summary(
            self.db,
            start_date=time_range[0],
            end_date=time_range[1],
            account_id=account_id
        )
        
        net_cash_flow = income_summary["total_income"] - expense_summary["total_expenses"]
        
        return {
            "intent": "cash_flow",
            "data": {
                "income": income_summary["total_income"],
                "expenses": expense_summary["total_expenses"],
                "net_cash_flow": net_cash_flow,
                "income_breakdown": income_summary["by_type"],
                "expense_breakdown": expense_summary["by_category"][:10],
            }
        }
    
    def handle_merchant(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle merchant-specific queries (e.g., 'how much at Starbucks?')"""
        time_range = parsed.get("time_range")
        merchant = parsed.get("merchant")
        account_filter = parsed.get("account_filter")
        account_id = None
        
        if account_filter:
            account = self.db.query(Account).filter(
                (Account.name.ilike(f"%{account_filter}%")) |
                (Account.id == account_filter)
            ).first()
            if account:
                account_id = account.id
        
        if not time_range:
            from datetime import timedelta
            time_range = (date.today() - timedelta(days=30), date.today())
        
        if not merchant:
            return {
                "error": "No merchant specified",
                "query": parsed.get("original_query"),
            }
        
        # Get transactions for this merchant
        query = self.db.query(Transaction).filter(
            Transaction.merchant_name.ilike(f"%{merchant}%"),
            Transaction.date >= time_range[0],
            Transaction.date <= time_range[1]
        )
        
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        
        transactions = query.order_by(Transaction.date.desc()).all()
        
        total = sum(abs(float(txn.amount)) for txn in transactions)
        
        return {
            "intent": "merchant",
            "merchant": merchant,
            "data": {
                "total": total,
                "count": len(transactions),
                "transactions": [
                    {
                        "date": txn.date.isoformat(),
                        "name": txn.name,
                        "amount": float(abs(txn.amount)),
                        "category": txn.expense_category or txn.primary_category,
                    }
                    for txn in transactions[:20]
                ],
            }
        }
