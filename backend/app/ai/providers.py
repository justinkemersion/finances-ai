"""AI provider implementations"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json

from .config import AIProvider


class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, api_key: str):
        """
        Initialize provider
        
        Args:
            api_key: API key for the provider
        """
        self.api_key = api_key
    
    @abstractmethod
    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Query the AI with a prompt and optional context
        
        Args:
            prompt: User's question/prompt
            context: Optional context data (will be formatted as JSON)
            
        Returns:
            AI response as string
        """
        pass
    
    @abstractmethod
    def format_context(self, context: Dict[str, Any]) -> str:
        """
        Format context data for the provider
        
        Args:
            context: Context data dictionary
            
        Returns:
            Formatted context string
        """
        pass


class OpenAIProvider(BaseAIProvider):
    """OpenAI (GPT) provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o-mini)
        """
        super().__init__(api_key)
        self.model = model
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )
    
    def format_context(self, context: Dict[str, Any]) -> str:
        """Format context as JSON string"""
        return json.dumps(context, indent=2)
    
    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Query OpenAI API"""
        # Build system message with context
        system_message = (
            "You are a helpful financial advisor analyzing personal finance data. "
            "You have access to the user's financial data in JSON format. "
            "Provide clear, actionable advice based on the data provided."
        )
        
        user_message = prompt
        if context:
            context_str = self.format_context(context)
            user_message = f"{prompt}\n\nFinancial Data:\n{context_str}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")


class AnthropicProvider(BaseAIProvider):
    """Anthropic (Claude) provider"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Anthropic provider
        
        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-5-sonnet-20241022)
        """
        super().__init__(api_key)
        self.model = model
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )
    
    def format_context(self, context: Dict[str, Any]) -> str:
        """Format context as JSON string"""
        return json.dumps(context, indent=2)
    
    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Query Anthropic API"""
        # Build system message
        system_message = (
            "You are a helpful financial advisor analyzing personal finance data. "
            "You have access to the user's financial data in JSON format. "
            "Provide clear, actionable advice based on the data provided."
        )
        
        user_message = prompt
        if context:
            context_str = self.format_context(context)
            user_message = f"{prompt}\n\nFinancial Data:\n{context_str}"
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_message,
                messages=[
                    {"role": "user", "content": user_message}
                ],
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")


def get_provider(provider_type: AIProvider, api_key: str, model: Optional[str] = None) -> BaseAIProvider:
    """
    Factory function to get a provider instance
    
    Args:
        provider_type: Type of provider
        api_key: API key
        model: Optional model name
        
    Returns:
        Provider instance
    """
    if provider_type == AIProvider.OPENAI:
        return OpenAIProvider(api_key, model=model or "gpt-4o-mini")
    elif provider_type == AIProvider.ANTHROPIC:
        return AnthropicProvider(api_key, model=model or "claude-3-5-sonnet-20241022")
    else:
        raise ValueError(f"Unsupported provider: {provider_type}")
