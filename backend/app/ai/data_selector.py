"""Intelligent data selection based on query intent"""

from typing import Dict, Any, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session

from ..queries.intent_router import IntentRouter, QueryIntent
from ..api.export import export_transactions, export_holdings, export_accounts


class DataSelector:
    """Selects relevant financial data based on query intent"""
    
    def __init__(self, db: Session):
        """
        Initialize data selector
        
        Args:
            db: Database session
        """
        self.db = db
    
    def select_data(self, query: str) -> Dict[str, Any]:
        """
        Select relevant data based on query intent
        
        Args:
            query: User's query
            
        Returns:
            Dictionary with selected financial data
        """
        # Parse query to understand intent
        parsed = IntentRouter.parse_query(query)
        intent = parsed["intent"]
        time_range = parsed.get("time_range")
        
        # Determine what data to include based on intent
        data = {
            "query": query,
            "intent": intent.value if intent else "unknown",
            "timestamp": date.today().isoformat(),
        }
        
        # Add relevant data based on intent
        if intent == QueryIntent.EXPENSES or intent == QueryIntent.SPENDING_CATEGORY:
            data["expenses"] = self._get_expense_data(time_range, parsed)
            data["summary"] = self._get_expense_summary(time_range)
        
        elif intent == QueryIntent.INCOME:
            data["income"] = self._get_income_data(time_range)
            data["summary"] = self._get_income_summary(time_range)
        
        elif intent == QueryIntent.CASH_FLOW:
            data["income"] = self._get_income_data(time_range)
            data["expenses"] = self._get_expense_data(time_range, parsed)
            data["cash_flow"] = self._get_cash_flow_summary(time_range)
        
        elif intent == QueryIntent.NET_WORTH:
            data["net_worth"] = self._get_net_worth_data()
            data["history"] = self._get_net_worth_history(time_range)
        
        elif intent == QueryIntent.PERFORMANCE:
            data["performance"] = self._get_performance_data(time_range)
            data["holdings"] = self._get_holdings_data()
        
        elif intent == QueryIntent.ALLOCATION:
            data["allocation"] = self._get_allocation_data()
            data["holdings"] = self._get_holdings_data()
        
        elif intent == QueryIntent.LUNCH:
            data["expenses"] = self._get_expense_data(time_range, parsed)
            data["lunch_analysis"] = self._get_lunch_data(time_range)
        
        elif intent == QueryIntent.MERCHANT:
            data["expenses"] = self._get_expense_data(time_range, parsed)
            data["merchants"] = self._get_merchant_data(time_range)
        
        else:
            # For unknown or general queries, include comprehensive summary
            data["summary"] = self._get_comprehensive_summary(time_range)
            data["net_worth"] = self._get_net_worth_data()
        
        return data
    
    def _get_expense_data(self, time_range: Optional[tuple], parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Get expense data"""
        start_date, end_date = time_range if time_range else (None, None)
        
        # Use export functionality to get expense data
        from ..api.export import export_transactions
        transactions = export_transactions(
            self.db,
            start_date=start_date,
            end_date=end_date,
            transaction_type="expense",
        )
        
        # Filter by category and merchant if specified
        if parsed.get("category"):
            transactions = [t for t in transactions if t.get("expense_category") == parsed.get("category")]
        if parsed.get("merchant"):
            transactions = [t for t in transactions if parsed.get("merchant").lower() in (t.get("merchant_name") or "").lower()]
        
        export_data = {"transactions": transactions}
        
        return {
            "transactions": export_data.get("transactions", []),
            "total_expenses": sum(
                abs(t.get("amount", 0)) 
                for t in export_data.get("transactions", [])
            ),
            "count": len(export_data.get("transactions", [])),
        }
    
    def _get_income_data(self, time_range: Optional[tuple]) -> Dict[str, Any]:
        """Get income data"""
        start_date, end_date = time_range if time_range else (None, None)
        
        from ..api.export import export_transactions
        transactions = export_transactions(
            self.db,
            start_date=start_date,
            end_date=end_date,
            transaction_type="income",
        )
        export_data = {"transactions": transactions}
        
        return {
            "transactions": export_data.get("transactions", []),
            "total_income": sum(
                t.get("amount", 0) 
                for t in export_data.get("transactions", [])
            ),
            "count": len(export_data.get("transactions", [])),
        }
    
    def _get_net_worth_data(self) -> Dict[str, Any]:
        """Get current net worth"""
        from ..analytics.net_worth import NetWorthAnalyzer
        return NetWorthAnalyzer.calculate_current_net_worth(self.db)
    
    def _get_net_worth_history(self, time_range: Optional[tuple]) -> list:
        """Get net worth history"""
        from ..analytics.net_worth import NetWorthAnalyzer
        
        if time_range:
            start_date, end_date = time_range
        else:
            start_date = date.today() - timedelta(days=90)
            end_date = date.today()
        
        return NetWorthAnalyzer.get_net_worth_history(
            self.db,
            start_date=start_date,
            end_date=end_date
        )
    
    def _get_performance_data(self, time_range: Optional[tuple]) -> Dict[str, Any]:
        """Get performance data"""
        from ..analytics.performance import PerformanceAnalyzer
        
        if time_range:
            start_date, _ = time_range
        else:
            start_date = date.today() - timedelta(days=30)
        
        return PerformanceAnalyzer.calculate_performance(
            self.db,
            start_date=start_date
        )
    
    def _get_allocation_data(self) -> Dict[str, Any]:
        """Get allocation data"""
        from ..analytics.allocation import AllocationAnalyzer
        return AllocationAnalyzer.calculate_allocation(self.db)
    
    def _get_holdings_data(self) -> list:
        """Get holdings data"""
        return export_holdings(self.db)
    
    def _get_expense_summary(self, time_range: Optional[tuple]) -> Dict[str, Any]:
        """Get expense summary"""
        from ..analytics.expenses import ExpenseAnalyzer
        
        if time_range:
            start_date, end_date = time_range
        else:
            start_date = date.today().replace(day=1)
            end_date = date.today()
        
        return ExpenseAnalyzer.calculate_expense_summary(
            self.db,
            start_date=start_date,
            end_date=end_date
        )
    
    def _get_income_summary(self, time_range: Optional[tuple]) -> Dict[str, Any]:
        """Get income summary"""
        from ..analytics.income import IncomeAnalyzer
        
        if time_range:
            start_date, end_date = time_range
        else:
            start_date = date.today().replace(month=1, day=1)
            end_date = date.today()
        
        return IncomeAnalyzer.calculate_income_summary(
            self.db,
            start_date=start_date,
            end_date=end_date
        )
    
    def _get_cash_flow_summary(self, time_range: Optional[tuple]) -> Dict[str, Any]:
        """Get cash flow summary"""
        income_summary = self._get_income_summary(time_range)
        expense_summary = self._get_expense_summary(time_range)
        
        return {
            "total_income": income_summary.get("total_income", 0),
            "total_expenses": expense_summary.get("total_expenses", 0),
            "net_cash_flow": income_summary.get("total_income", 0) - expense_summary.get("total_expenses", 0),
        }
    
    def _get_lunch_data(self, time_range: Optional[tuple]) -> Dict[str, Any]:
        """Get lunch-specific data"""
        from ..queries.handlers import QueryHandler
        
        handler = QueryHandler(self.db)
        result = handler.handle_lunch(IntentRouter.parse_query("lunch spending"))
        
        return {
            "total_lunch_spending": result.get("total", 0),
            "transaction_count": result.get("count", 0),
            "average_per_lunch": result.get("average", 0),
        }
    
    def _get_merchant_data(self, time_range: Optional[tuple]) -> list:
        """Get merchant data"""
        from ..analytics.expenses import ExpenseAnalyzer
        
        if time_range:
            start_date, end_date = time_range
        else:
            start_date = date.today().replace(day=1)
            end_date = date.today()
        
        return ExpenseAnalyzer.get_top_merchants(
            self.db,
            limit=20,
            start_date=start_date,
            end_date=end_date
        )
    
    def _get_comprehensive_summary(self, time_range: Optional[tuple]) -> Dict[str, Any]:
        """Get comprehensive summary for general queries"""
        return {
            "net_worth": self._get_net_worth_data(),
            "income_summary": self._get_income_summary(time_range),
            "expense_summary": self._get_expense_summary(time_range),
            "cash_flow": self._get_cash_flow_summary(time_range),
        }
