"""Factory for creating provider clients and sync handlers"""

from typing import Optional
from .base import BaseProviderClient, BaseProviderSync, ProviderType
from .plaid_client import PlaidClient
from .plaid_sync import PlaidSync
from ..config import config

# Optional Teller imports (only if SDK is installed)
try:
    from .teller_client import TellerClient
    from .teller_sync import TellerSync
    TELLER_AVAILABLE = True
except ImportError:
    TELLER_AVAILABLE = False
    TellerClient = None
    TellerSync = None


class ProviderFactory:
    """Factory for creating provider instances"""
    
    @staticmethod
    def create_client(
        provider: Optional[ProviderType] = None,
        **kwargs
    ) -> BaseProviderClient:
        """
        Create a provider client instance
        
        Args:
            provider: Provider type (defaults to config.DEFAULT_PROVIDER)
            **kwargs: Provider-specific configuration
            
        Returns:
            Provider client instance
        """
        if provider is None:
            provider = ProviderFactory.from_string(config.DEFAULT_PROVIDER)
        
        if provider == ProviderType.PLAID:
            return PlaidClient(**kwargs)
        elif provider == ProviderType.TELLER:
            if not TELLER_AVAILABLE:
                raise ImportError(
                    "Teller SDK not installed. Install with: pip install teller-python"
                )
            return TellerClient(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def create_sync(
        provider: Optional[ProviderType] = None,
        provider_client: Optional[BaseProviderClient] = None,
        **kwargs
    ) -> BaseProviderSync:
        """
        Create a provider sync handler instance
        
        Args:
            provider: Provider type (defaults to config.DEFAULT_PROVIDER)
            provider_client: Optional provider client (creates new if not provided)
            **kwargs: Provider-specific configuration
            
        Returns:
            Provider sync handler instance
        """
        if provider_client is None:
            provider_client = ProviderFactory.create_client(provider, **kwargs)
        
        if isinstance(provider_client, PlaidClient):
            return PlaidSync(provider_client)
        elif TELLER_AVAILABLE and isinstance(provider_client, TellerClient):
            return TellerSync(provider_client)
        else:
            # Determine provider from client type
            if provider is None:
                provider = ProviderFactory.from_string(config.DEFAULT_PROVIDER)
            
            if provider == ProviderType.PLAID:
                return PlaidSync(provider_client)
            elif provider == ProviderType.TELLER:
                if not TELLER_AVAILABLE:
                    raise ImportError(
                        "Teller SDK not installed. Install with: pip install teller-python"
                    )
                return TellerSync(provider_client)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def from_string(provider_str: str) -> ProviderType:
        """
        Convert string to ProviderType
        
        Args:
            provider_str: Provider name as string
            
        Returns:
            ProviderType enum value
        """
        provider_str = provider_str.lower().strip()
        try:
            return ProviderType(provider_str)
        except ValueError:
            raise ValueError(
                f"Unknown provider: {provider_str}. "
                f"Supported providers: {[p.value for p in ProviderType]}"
            )
