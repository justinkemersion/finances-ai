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
        elif intent == QueryIntent.LUNCH:
            return self.handle_lunch(parsed)
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
                    "How much did I spend on lunch?",
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
    
    def calculate_lunch_confidence(self, txn: Transaction) -> Dict[str, Any]:
        """
        Calculate confidence score that a transaction is actually lunch
        
        Returns dict with:
        - confidence: 0-100 score
        - reasons: list of factors affecting confidence
        - is_likely_lunch: boolean
        """
        from sqlalchemy import extract
        from datetime import time
        
        confidence = 50  # Start neutral
        reasons = []
        amount = abs(float(txn.amount))
        merchant = (txn.merchant_name or txn.name or "").lower()
        
        # Check if it's a grocery store
        is_grocery = any(grocery in merchant for grocery in IntentRouter.GROCERY_STORES)
        # Check if it's a gas station
        is_gas_station = any(gas in merchant for gas in IntentRouter.GAS_STATIONS)
        # Check if it's a known lunch merchant
        is_lunch_merchant = any(lunch in merchant for lunch in IntentRouter.LUNCH_MERCHANTS)
        
        # Time-based scoring
        if txn.transaction_datetime:
            hour = txn.transaction_datetime.hour
            if 11 <= hour <= 14:  # Lunch hours
                confidence += 30
                reasons.append(f"Lunch time ({hour}:{txn.transaction_datetime.minute:02d})")
            elif 8 <= hour <= 10 or 15 <= hour <= 16:  # Near lunch hours
                confidence += 10
                reasons.append(f"Near lunch time ({hour}:{txn.transaction_datetime.minute:02d})")
            else:
                confidence -= 20
                reasons.append(f"Outside lunch hours ({hour}:{txn.transaction_datetime.minute:02d})")
        else:
            reasons.append("No time data available")
        
        # Merchant-based scoring
        if is_lunch_merchant:
            confidence += 40
            reasons.append("Known lunch merchant")
        elif is_grocery:
            # Grocery stores need amount filtering
            if amount <= IntentRouter.GROCERY_LUNCH_THRESHOLD:
                confidence += 20
                reasons.append(f"Grocery store, small amount (${amount:.2f})")
            else:
                confidence -= 50
                reasons.append(f"Grocery store, large amount (${amount:.2f}) - likely full shopping")
        elif is_gas_station:
            # Gas stations: small amount = food, large amount = gas
            if amount <= IntentRouter.GAS_FOOD_THRESHOLD:
                confidence += 25
                reasons.append(f"Gas station, small amount (${amount:.2f}) - likely food")
            else:
                confidence -= 40
                reasons.append(f"Gas station, large amount (${amount:.2f}) - likely gas purchase")
        else:
            # Unknown merchant, rely on other factors
            confidence -= 10
            reasons.append("Unknown merchant type")
        
        # Amount-based scoring
        if amount <= IntentRouter.LUNCH_MAX_AMOUNT:
            confidence += 15
            reasons.append(f"Typical lunch amount (${amount:.2f})")
        elif amount <= 25:
            confidence += 5
            reasons.append(f"Moderate amount (${amount:.2f})")
        else:
            confidence -= 30
            reasons.append(f"Large amount (${amount:.2f}) - unlikely to be lunch")
        
        # Category-based scoring
        if txn.expense_category in ["restaurants", "food"]:
            confidence += 10
            reasons.append("Restaurant/food category")
        elif txn.primary_category and "FOOD" in txn.primary_category:
            confidence += 10
            reasons.append("Food category")
        elif is_grocery and amount > IntentRouter.GROCERY_LUNCH_THRESHOLD:
            # Large grocery purchase is definitely not lunch
            confidence -= 20
            reasons.append("Large grocery purchase")
        
        # Clamp confidence to 0-100
        confidence = max(0, min(100, confidence))
        
        # Determine if likely lunch (threshold: 60)
        is_likely_lunch = confidence >= 60
        
        return {
            "confidence": confidence,
            "reasons": reasons,
            "is_likely_lunch": is_likely_lunch,
            "amount": amount,
            "merchant": merchant,
        }
    
    def handle_lunch(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """Handle lunch spending queries - smart detection using time, merchant, and amount"""
        time_range = parsed.get("time_range")
        account_filter = parsed.get("account_filter")
        account_id = None
        show_uncertain = parsed.get("show_uncertain", False)  # Future: allow showing uncertain transactions
        
        if account_filter:
            account = self.db.query(Account).filter(
                (Account.name.ilike(f"%{account_filter}%")) |
                (Account.id == account_filter)
            ).first()
            if account:
                account_id = account.id
        
        if not time_range:
            from datetime import timedelta
            time_range = (date.today() - timedelta(days=60), date.today())  # Default 2 months
        
        # Build query for potential lunch transactions
        # Strategy: Cast a wider net, then filter by confidence
        from sqlalchemy import or_, func, extract
        
        query = self.db.query(Transaction).filter(
            Transaction.is_expense == True,
            Transaction.date >= time_range[0],
            Transaction.date <= time_range[1]
        )
        
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        
        # Initial filter: time-based OR merchant-based OR category-based
        lunch_conditions = []
        
        # Time-based: lunch hours
        lunch_conditions.append(
            (Transaction.transaction_datetime.isnot(None)) &
            (extract('hour', Transaction.transaction_datetime) >= 11) &
            (extract('hour', Transaction.transaction_datetime) <= 14)
        )
        
        # Known lunch merchants
        lunch_merchant_patterns = IntentRouter.LUNCH_MERCHANTS
        merchant_conditions = []
        for merchant in lunch_merchant_patterns:
            merchant_conditions.append(Transaction.merchant_name.ilike(f"%{merchant}%"))
            merchant_conditions.append(Transaction.name.ilike(f"%{merchant}%"))
        
        # Grocery stores with small amounts (potential lunch)
        grocery_conditions = []
        for grocery in IntentRouter.GROCERY_STORES:
            grocery_conditions.append(
                (Transaction.merchant_name.ilike(f"%{grocery}%")) |
                (Transaction.name.ilike(f"%{grocery}%"))
            )
        if grocery_conditions:
            # Only include grocery stores with small amounts
            lunch_conditions.append(
                or_(*grocery_conditions) &
                (func.abs(Transaction.amount) <= IntentRouter.GROCERY_LUNCH_THRESHOLD)
            )
        
        # Gas stations with small amounts (potential food)
        gas_conditions = []
        for gas in IntentRouter.GAS_STATIONS:
            gas_conditions.append(
                (Transaction.merchant_name.ilike(f"%{gas}%")) |
                (Transaction.name.ilike(f"%{gas}%"))
            )
        if gas_conditions:
            # Only include gas stations with small amounts
            lunch_conditions.append(
                or_(*gas_conditions) &
                (func.abs(Transaction.amount) <= IntentRouter.GAS_FOOD_THRESHOLD)
            )
        
        # Restaurant/food categories
        category_conditions = [
            Transaction.expense_category.in_(["restaurants", "food"]),
            Transaction.primary_category.ilike("%FOOD%"),
            Transaction.detailed_category.ilike("%RESTAURANT%"),
            Transaction.detailed_category.ilike("%FOOD%"),
        ]
        
        # Combine all conditions
        if merchant_conditions:
            lunch_conditions.append(or_(*merchant_conditions))
        lunch_conditions.append(or_(*category_conditions))
        
        # Apply the filter
        query = query.filter(or_(*lunch_conditions))
        
        # Get all potential transactions
        all_transactions = query.order_by(Transaction.date.desc()).all()
        
        # Calculate confidence for each and filter
        lunch_transactions = []
        uncertain_transactions = []
        
        for txn in all_transactions:
            confidence_data = self.calculate_lunch_confidence(txn)
            
            if confidence_data["is_likely_lunch"]:
                lunch_transactions.append((txn, confidence_data))
            elif confidence_data["confidence"] >= 40:  # Somewhat uncertain
                uncertain_transactions.append((txn, confidence_data))
        
        # Calculate totals
        total = sum(abs(float(txn.amount)) for txn, _ in lunch_transactions)
        uncertain_total = sum(abs(float(txn.amount)) for txn, _ in uncertain_transactions)
        
        # Group by merchant for breakdown
        merchant_totals = {}
        for txn, conf_data in lunch_transactions:
            merchant = txn.merchant_name or txn.name
            if merchant not in merchant_totals:
                merchant_totals[merchant] = {"count": 0, "total": 0.0, "avg_confidence": 0.0}
            merchant_totals[merchant]["count"] += 1
            merchant_totals[merchant]["total"] += abs(float(txn.amount))
            merchant_totals[merchant]["avg_confidence"] += conf_data["confidence"]
        
        # Calculate average confidence per merchant
        for merchant in merchant_totals:
            merchant_totals[merchant]["avg_confidence"] /= merchant_totals[merchant]["count"]
        
        # Sort merchants by total
        merchant_breakdown = sorted(
            [{"merchant": k, **{key: v for key, v in v.items() if key != "avg_confidence"}, 
              "confidence": round(v["avg_confidence"], 1)} for k, v in merchant_totals.items()],
            key=lambda x: x["total"],
            reverse=True
        )
        
        return {
            "intent": "lunch",
            "data": {
                "total": total,
                "count": len(lunch_transactions),
                "uncertain_count": len(uncertain_transactions),
                "uncertain_total": uncertain_total,
                "merchant_breakdown": merchant_breakdown,
                "transactions": [
                    {
                        "date": txn.date.isoformat(),
                        "time": txn.transaction_datetime.strftime("%H:%M") if txn.transaction_datetime else None,
                        "name": txn.name,
                        "merchant": txn.merchant_name,
                        "amount": float(abs(txn.amount)),
                        "category": txn.expense_category or txn.primary_category,
                        "confidence": round(conf_data["confidence"], 1),
                        "confidence_reasons": conf_data["reasons"][:3],  # Top 3 reasons
                    }
                    for txn, conf_data in lunch_transactions[:30]  # Limit to 30 for display
                ],
                "uncertain_transactions": [
                    {
                        "date": txn.date.isoformat(),
                        "time": txn.transaction_datetime.strftime("%H:%M") if txn.transaction_datetime else None,
                        "name": txn.name,
                        "merchant": txn.merchant_name,
                        "amount": float(abs(txn.amount)),
                        "confidence": round(conf_data["confidence"], 1),
                        "confidence_reasons": conf_data["reasons"],
                    }
                    for txn, conf_data in uncertain_transactions[:10]  # Show top 10 uncertain
                ] if uncertain_transactions else [],
            }
        }
