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
        
        # Check patterns in order of specificity
        for pattern in cls.PERFORMANCE_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.PERFORMANCE
        
        for pattern in cls.ALLOCATION_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.ALLOCATION
        
        for pattern in cls.HOLDINGS_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.HOLDINGS
        
        for pattern in cls.TRANSACTIONS_PATTERNS:
            if re.search(pattern, query_lower):
                return QueryIntent.TRANSACTIONS
        
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
        
        return {
            "intent": intent,
            "time_range": time_range,
            "account_filter": account_filter,
            "original_query": query,
        }
