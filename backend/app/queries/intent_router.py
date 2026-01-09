"""Intent-based query routing"""

import re
from typing import Dict, Any, Optional, List
from datetime import date, timedelta
from enum import Enum


class QueryIntent(Enum):
    """Supported query intents"""
    NET_WORTH = "net_worth"
    PERFORMANCE = "performance"
    ALLOCATION = "allocation"
    HOLDINGS = "holdings"
    TRANSACTIONS = "transactions"
    INCOME = "income"
    EXPENSES = "expenses"
    SPENDING_CATEGORY = "spending_category"
    DIVIDENDS = "dividends"
    CASH_FLOW = "cash_flow"
    MERCHANT = "merchant"
    UNKNOWN = "unknown"


class IntentRouter:
    """Routes natural language queries to appropriate handlers"""
    
    # Intent patterns
    NET_WORTH_PATTERNS = [
        r"net\s+worth",
        r"how\s+much\s+am\s+i\s+worth",
        r"total\s+value",
        r"portfolio\s+value",
        r"assets",
    ]
    
    PERFORMANCE_PATTERNS = [
        r"performance",
        r"how\s+did\s+(my\s+)?portfolio\s+do",
        r"return",
        r"gain",
        r"loss",
        r"profit",
        r"how\s+much\s+did\s+i\s+(make|earn|lose)",
    ]
    
    ALLOCATION_PATTERNS = [
        r"allocation",
        r"breakdown",
        r"distribution",
        r"what\s+am\s+i\s+invested\s+in",
        r"holdings",
        r"top\s+holdings",
    ]
    
    HOLDINGS_PATTERNS = [
        r"holdings",
        r"stocks",
        r"securities",
        r"what\s+do\s+i\s+own",
    ]
    
    TRANSACTIONS_PATTERNS = [
        r"transactions",
        r"trades",
        r"activity",
        r"what\s+did\s+i\s+(buy|sell)",
    ]
    
    INCOME_PATTERNS = [
        r"income",
        r"salary",
        r"paystub",
        r"paycheck",
        r"earnings",
        r"how\s+much\s+did\s+i\s+earn",
        r"how\s+much\s+do\s+i\s+make",
        r"revenue",
        r"payroll",
    ]
    
    EXPENSES_PATTERNS = [
        r"expenses",
        r"spending",
        r"spent",
        r"costs",
        r"how\s+much\s+did\s+i\s+spend",
        r"what\s+did\s+i\s+spend",
        r"outgoings",
        r"outflow",
    ]
    
    SPENDING_CATEGORY_PATTERNS = [
        r"spent\s+on\s+(\w+)",
        r"(\w+)\s+spending",
        r"how\s+much\s+(?:did\s+i\s+)?spend\s+on\s+(\w+)",
        r"(\w+)\s+expenses",
        r"(\w+)\s+costs",
    ]
    
    DIVIDENDS_PATTERNS = [
        r"dividends",
        r"dividend\s+income",
        r"dividend\s+payout",
        r"how\s+much\s+in\s+dividends",
    ]
    
    CASH_FLOW_PATTERNS = [
        r"cash\s+flow",
        r"income\s+vs\s+expenses",
        r"money\s+in\s+vs\s+out",
        r"profit\s+and\s+loss",
        r"p&l",
        r"earnings\s+vs\s+spending",
    ]
    
    MERCHANT_PATTERNS = [
        r"spent\s+at\s+(\w+)",
        r"(\w+)\s+transactions",
        r"how\s+much\s+at\s+(\w+)",
        r"purchases\s+from\s+(\w+)",
    ]
    
    TIME_PATTERNS = [
        (r"last\s+month", lambda: (date.today() - timedelta(days=30), date.today())),
        (r"this\s+month", lambda: (date.today().replace(day=1), date.today())),
        (r"last\s+(\d+)\s+months?", lambda m: (date.today() - timedelta(days=int(m.group(1)) * 30), date.today())),
        (r"last\s+year", lambda: (date.today() - timedelta(days=365), date.today())),
        (r"this\s+year", lambda: (date.today().replace(month=1, day=1), date.today())),
        (r"last\s+(\d+)\s+days?", lambda m: (date.today() - timedelta(days=int(m.group(1))), date.today())),
        (r"yesterday", lambda: (date.today() - timedelta(days=1), date.today() - timedelta(days=1))),
        (r"today", lambda: (date.today(), date.today())),
    ]
    
    # Common spending category aliases
    CATEGORY_ALIASES = {
        "beer": ["beer", "alcohol", "bar", "brewery", "pub", "liquor", "wine", "drinks"],
        "restaurants": ["restaurant", "dining", "food", "eat", "cafe", "coffee", "lunch", "dinner"],
        "gas": ["gas", "fuel", "gasoline", "petrol", "filling station"],
        "groceries": ["grocery", "supermarket", "food store", "grocery store"],
        "bills": ["bill", "utility", "electric", "water", "internet", "phone", "cable"],
        "entertainment": ["entertainment", "movie", "theater", "concert", "streaming"],
        "shopping": ["shopping", "retail", "store", "amazon", "online"],
        "transport": ["transport", "uber", "lyft", "taxi", "transit", "bus", "train"],
        "health": ["health", "medical", "doctor", "pharmacy", "gym", "fitness"],
    }
    
    @classmethod
    def parse_intent(cls, query: str) -> QueryIntent:
        """
        Parse query intent from natural language
        
        Args:
            query: Natural language query
            
        Returns:
            QueryIntent enum
        """
        query_lower = query.lower()
        
        # Check patterns in order of specificity (most specific first)
        # Spending category patterns (very specific)
        for pattern in cls.SPENDING_CATEGORY_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.SPENDING_CATEGORY
        
        # Merchant patterns (very specific)
        for pattern in cls.MERCHANT_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.MERCHANT
        
        # Dividends (specific investment query)
        for pattern in cls.DIVIDENDS_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.DIVIDENDS
        
        # Cash flow (specific financial query)
        for pattern in cls.CASH_FLOW_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.CASH_FLOW
        
        # Performance (investment-focused)
        for pattern in cls.PERFORMANCE_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.PERFORMANCE
        
        # Income (general)
        for pattern in cls.INCOME_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.INCOME
        
        # Expenses (general)
        for pattern in cls.EXPENSES_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.EXPENSES
        
        # Allocation (investment-focused)
        for pattern in cls.ALLOCATION_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.ALLOCATION
        
        # Holdings (investment-focused)
        for pattern in cls.HOLDINGS_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.HOLDINGS
        
        # Transactions (general)
        for pattern in cls.TRANSACTIONS_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.TRANSACTIONS
        
        # Net worth (general)
        for pattern in cls.NET_WORTH_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.NET_WORTH
        
        return QueryIntent.UNKNOWN
    
    @classmethod
    def extract_time_range(cls, query: str) -> Optional[tuple[date, date]]:
        """
        Extract time range from query
        
        Args:
            query: Natural language query
            
        Returns:
            Tuple of (start_date, end_date) or None
        """
        query_lower = query.lower()
        
        for pattern, handler in cls.TIME_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    if callable(handler):
                        return handler()
                    else:
                        return handler(match)
                except Exception:
                    continue
        
        return None
    
    @classmethod
    def extract_account_filter(cls, query: str) -> Optional[str]:
        """
        Extract account filter from query (basic implementation)
        
        Args:
            query: Natural language query
            
        Returns:
            Account ID or name if found, None otherwise
        """
        # This is a basic implementation - could be enhanced with NLP
        # For now, just look for account names in quotes or after "in account"
        account_match = re.search(r'in\s+account\s+"?([^"]+)"?', query.lower())
        if account_match:
            return account_match.group(1)
        
        return None
    
    @classmethod
    def extract_category(cls, query: str) -> Optional[str]:
        """
        Extract spending category from query
        
        Args:
            query: Natural language query
            
        Returns:
            Category name if found, None otherwise
        """
        query_lower = query.lower()
        
        # Try to extract from spending category patterns
        for pattern in cls.SPENDING_CATEGORY_PATTERNS:
            match = re.search(pattern, query_lower)
            if match and match.groups():
                category = match.group(1).lower()
                # Check if it's a known alias
                for main_category, aliases in cls.CATEGORY_ALIASES.items():
                    if category in aliases or category == main_category:
                        return main_category
                return category
        
        # Check for direct category mentions
        for main_category, aliases in cls.CATEGORY_ALIASES.items():
            for alias in aliases:
                if re.search(rf'\b{alias}\b', query_lower):
                    return main_category
        
        return None
    
    @classmethod
    def extract_merchant(cls, query: str) -> Optional[str]:
        """
        Extract merchant name from query
        
        Args:
            query: Natural language query
            
        Returns:
            Merchant name if found, None otherwise
        """
        query_lower = query.lower()
        
        # Try to extract from merchant patterns
        for pattern in cls.MERCHANT_PATTERNS:
            match = re.search(pattern, query_lower)
            if match and match.groups():
                return match.group(1)
        
        # Look for "at [merchant]" or "from [merchant]"
        merchant_match = re.search(r'(?:at|from)\s+([a-z0-9\s]+?)(?:\s|$|,|\.)', query_lower)
        if merchant_match:
            return merchant_match.group(1).strip()
        
        return None
    
    @classmethod
    def extract_amount_threshold(cls, query: str) -> Optional[float]:
        """
        Extract amount threshold from query (e.g., "more than $100")
        
        Args:
            query: Natural language query
            
        Returns:
            Amount threshold if found, None otherwise
        """
        query_lower = query.lower()
        
        # Patterns for amount thresholds
        patterns = [
            r'(?:more|greater|over|above)\s+(?:than\s+)?\$?(\d+(?:\.\d+)?)',
            r'(?:less|under|below)\s+(?:than\s+)?\$?(\d+(?:\.\d+)?)',
            r'\$(\d+(?:\.\d+)?)\s+(?:or\s+)?(?:more|greater|over)',
            r'\$(\d+(?:\.\d+)?)\s+(?:or\s+)?(?:less|under)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        return None
    
    @classmethod
    def parse_query(cls, query: str) -> Dict[str, Any]:
        """
        Parse a natural language query into structured parameters
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary with parsed query parameters
        """
        intent = cls.parse_intent(query)
        time_range = cls.extract_time_range(query)
        account_filter = cls.extract_account_filter(query)
        category = cls.extract_category(query)
        merchant = cls.extract_merchant(query)
        amount_threshold = cls.extract_amount_threshold(query)
        
        return {
            "intent": intent,
            "time_range": time_range,
            "account_filter": account_filter,
            "category": category,
            "merchant": merchant,
            "amount_threshold": amount_threshold,
            "original_query": query,
        }
