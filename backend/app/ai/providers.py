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
    
    # Available Anthropic models
    AVAILABLE_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-sonnet-20240620",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
    ]
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Anthropic provider
        
        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-5-sonnet-20241022)
                   Options: claude-3-5-sonnet-20241022, claude-3-opus-20240229, 
                            claude-3-sonnet-20240229, claude-3-haiku-20240307
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


class GoogleProvider(BaseAIProvider):
    """Google (Gemini) provider"""
    
    # Available Google models
    AVAILABLE_MODELS = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-pro",
        "gemini-1.0-pro",
    ]
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        """
        Initialize Google provider
        
        Args:
            api_key: Google API key
            model: Model to use (default: gemini-1.5-pro)
                   Options: gemini-1.5-pro, gemini-1.5-flash, gemini-pro, gemini-1.0-pro
        """
        super().__init__(api_key)
        self.model = model
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(model)
        except ImportError:
            raise ImportError(
                "google-generativeai package is required. Install with: pip install google-generativeai"
            )
    
    def format_context(self, context: Dict[str, Any]) -> str:
        """Format context as JSON string"""
        return json.dumps(context, indent=2)
    
    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Query Google Gemini API"""
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
        
        # Combine system and user message
        full_prompt = f"{system_message}\n\n{user_message}"
        
        try:
            response = self.client.generate_content(full_prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Google Gemini API error: {str(e)}")


class CohereProvider(BaseAIProvider):
    """Cohere provider"""
    
    # Available Cohere models
    AVAILABLE_MODELS = [
        "command-r-plus",
        "command-r",
        "command",
        "command-light",
        "command-nightly",
    ]
    
    def __init__(self, api_key: str, model: str = "command-r-plus"):
        """
        Initialize Cohere provider
        
        Args:
            api_key: Cohere API key
            model: Model to use (default: command-r-plus)
                   Options: command-r-plus, command-r, command, command-light, command-nightly
        """
        super().__init__(api_key)
        self.model = model
        try:
            import cohere
            self.client = cohere.Client(api_key=api_key)
        except ImportError:
            raise ImportError(
                "cohere package is required. Install with: pip install cohere"
            )
    
    def format_context(self, context: Dict[str, Any]) -> str:
        """Format context as JSON string"""
        return json.dumps(context, indent=2)
    
    def query(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Query Cohere API"""
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
            response = self.client.chat(
                model=self.model,
                message=user_message,
                preamble=system_message,
            )
            return response.text
        except Exception as e:
            raise Exception(f"Cohere API error: {str(e)}")


def get_provider(provider_type: AIProvider, api_key: str, model: Optional[str] = None) -> BaseAIProvider:
    """
    Factory function to get a provider instance
    
    Args:
        provider_type: Type of provider
        api_key: API key
        model: Optional model name (if None, uses provider default)
        
    Returns:
        Provider instance
    """
    # Default models for each provider
    default_models = {
        AIProvider.OPENAI: "gpt-4o-mini",
        AIProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
        AIProvider.GOOGLE: "gemini-1.5-pro",
        AIProvider.COHERE: "command-r-plus",
    }
    
    if provider_type == AIProvider.OPENAI:
        return OpenAIProvider(api_key, model=model or default_models[AIProvider.OPENAI])
    elif provider_type == AIProvider.ANTHROPIC:
        return AnthropicProvider(api_key, model=model or default_models[AIProvider.ANTHROPIC])
    elif provider_type == AIProvider.GOOGLE:
        return GoogleProvider(api_key, model=model or default_models[AIProvider.GOOGLE])
    elif provider_type == AIProvider.COHERE:
        return CohereProvider(api_key, model=model or default_models[AIProvider.COHERE])
    else:
        raise ValueError(f"Unsupported provider: {provider_type}")
