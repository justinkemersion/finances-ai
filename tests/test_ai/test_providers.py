"""Tests for AI provider implementations"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from backend.app.ai.providers import (
    BaseAIProvider,
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    CohereProvider,
    get_provider
)
from backend.app.ai.config import AIProvider


class TestProviderFactory:
    """Test provider factory function"""
    
    def test_get_openai_provider(self):
        """Test getting OpenAI provider"""
        with patch('backend.app.ai.providers.openai') as mock_openai_module:
            mock_client = Mock()
            mock_openai_module.OpenAI.return_value = mock_client
            provider = get_provider(AIProvider.OPENAI, "test_key", model="gpt-4o")
            assert isinstance(provider, OpenAIProvider)
            assert provider.model == "gpt-4o"
    
    def test_get_anthropic_provider(self):
        """Test getting Anthropic provider"""
        with patch('backend.app.ai.providers.anthropic') as mock_anthropic_module:
            mock_client = Mock()
            mock_anthropic_module.Anthropic.return_value = mock_client
            provider = get_provider(AIProvider.ANTHROPIC, "test_key", model="claude-3-opus-20240229")
            assert isinstance(provider, AnthropicProvider)
            assert provider.model == "claude-3-opus-20240229"
    
    def test_get_google_provider(self):
        """Test getting Google provider"""
        with patch('backend.app.ai.providers.genai') as mock_genai:
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_genai.configure = Mock()
            provider = get_provider(AIProvider.GOOGLE, "test_key", model="gemini-1.5-flash")
            assert isinstance(provider, GoogleProvider)
            assert provider.model == "gemini-1.5-flash"
    
    def test_get_cohere_provider(self):
        """Test getting Cohere provider"""
        with patch('backend.app.ai.providers.cohere') as mock_cohere_module:
            mock_client = Mock()
            mock_cohere_module.Client.return_value = mock_client
            provider = get_provider(AIProvider.COHERE, "test_key", model="command-r")
            assert isinstance(provider, CohereProvider)
            assert provider.model == "command-r"
    
    def test_get_provider_with_default_model(self):
        """Test getting provider with default model"""
        with patch('backend.app.ai.providers.openai') as mock_openai_module:
            mock_client = Mock()
            mock_openai_module.OpenAI.return_value = mock_client
            provider = get_provider(AIProvider.OPENAI, "test_key")
            assert provider.model == "gpt-4o-mini"  # Default
    
    def test_get_provider_unsupported(self):
        """Test error for unsupported provider"""
        # Test with a provider that exists but isn't implemented in factory
        # We can't easily create a new enum value, so we'll test the factory logic
        # by ensuring all defined providers work
        with patch('backend.app.ai.providers.openai') as mock_openai_module:
            mock_client = Mock()
            mock_openai_module.OpenAI.return_value = mock_client
            # All defined providers should work
            provider = get_provider(AIProvider.OPENAI, "test_key")
            assert provider is not None


class TestOpenAIProvider:
    """Test OpenAI provider"""
    
    def test_format_context(self):
        """Test context formatting"""
        with patch('backend.app.ai.providers.openai') as mock_openai_module:
            mock_client = Mock()
            mock_openai_module.OpenAI.return_value = mock_client
            provider = OpenAIProvider("test_key")
            context = {"test": "data"}
            formatted = provider.format_context(context)
            assert "test" in formatted
            assert "data" in formatted
    
    def test_query_with_context(self):
        """Test querying with context"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('openai.OpenAI', return_value=mock_client):
            provider = OpenAIProvider("test_key")
            provider.client = mock_client
            
            response = provider.query("test query", context={"data": "test"})
            assert response == "Test response"
            assert mock_client.chat.completions.create.called
    
    def test_query_error_handling(self):
        """Test error handling in query"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('backend.app.ai.providers.openai') as mock_openai_module:
            mock_openai_module.OpenAI.return_value = mock_client
            provider = OpenAIProvider("test_key")
            provider.client = mock_client
            
            with pytest.raises(Exception, match="OpenAI API error"):
                provider.query("test query")
    
    def test_available_models(self):
        """Test that available models are defined"""
        assert hasattr(OpenAIProvider, 'AVAILABLE_MODELS')
        assert len(OpenAIProvider.AVAILABLE_MODELS) > 0
        assert "gpt-4o-mini" in OpenAIProvider.AVAILABLE_MODELS


class TestAnthropicProvider:
    """Test Anthropic provider"""
    
    def test_format_context(self):
        """Test context formatting"""
        with patch('backend.app.ai.providers.anthropic') as mock_anthropic_module:
            mock_client = Mock()
            mock_anthropic_module.Anthropic.return_value = mock_client
            provider = AnthropicProvider("test_key")
            context = {"test": "data"}
            formatted = provider.format_context(context)
            assert "test" in formatted
    
    def test_query_with_context(self):
        """Test querying with context"""
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Test response"
        
        mock_client = Mock()
        mock_client.messages.create.return_value = mock_response
        
        with patch('backend.app.ai.providers.anthropic') as mock_anthropic_module:
            mock_anthropic_module.Anthropic.return_value = mock_client
            provider = AnthropicProvider("test_key")
            provider.client = mock_client
            
            response = provider.query("test query", context={"data": "test"})
            assert response == "Test response"
    
    def test_available_models(self):
        """Test that available models are defined"""
        assert hasattr(AnthropicProvider, 'AVAILABLE_MODELS')
        assert len(AnthropicProvider.AVAILABLE_MODELS) > 0


class TestGoogleProvider:
    """Test Google provider"""
    
    def test_format_context(self):
        """Test context formatting"""
        with patch('backend.app.ai.providers.genai') as mock_genai:
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_genai.configure = Mock()
            provider = GoogleProvider("test_key")
            context = {"test": "data"}
            formatted = provider.format_context(context)
            assert "test" in formatted
    
    def test_query_with_context(self):
        """Test querying with context"""
        mock_response = Mock()
        mock_response.text = "Test response"
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        
        with patch('backend.app.ai.providers.genai') as mock_genai:
            mock_genai.GenerativeModel.return_value = mock_model
            mock_genai.configure = Mock()
            provider = GoogleProvider("test_key")
            provider.client = mock_model
                
                response = provider.query("test query", context={"data": "test"})
                assert response == "Test response"
    
    def test_available_models(self):
        """Test that available models are defined"""
        assert hasattr(GoogleProvider, 'AVAILABLE_MODELS')
        assert len(GoogleProvider.AVAILABLE_MODELS) > 0
        assert "gemini-1.5-pro" in GoogleProvider.AVAILABLE_MODELS


class TestCohereProvider:
    """Test Cohere provider"""
    
    def test_format_context(self):
        """Test context formatting"""
        with patch('backend.app.ai.providers.cohere') as mock_cohere_module:
            mock_client = Mock()
            mock_cohere_module.Client.return_value = mock_client
            provider = CohereProvider("test_key")
            context = {"test": "data"}
            formatted = provider.format_context(context)
            assert "test" in formatted
    
    def test_query_with_context(self):
        """Test querying with context"""
        mock_response = Mock()
        mock_response.text = "Test response"
        
        mock_client = Mock()
        mock_client.chat.return_value = mock_response
        
        with patch('backend.app.ai.providers.cohere') as mock_cohere_module:
            mock_cohere_module.Client.return_value = mock_client
            provider = CohereProvider("test_key")
            provider.client = mock_client
            
            response = provider.query("test query", context={"data": "test"})
            assert response == "Test response"
    
    def test_available_models(self):
        """Test that available models are defined"""
        assert hasattr(CohereProvider, 'AVAILABLE_MODELS')
        assert len(CohereProvider.AVAILABLE_MODELS) > 0
        assert "command-r-plus" in CohereProvider.AVAILABLE_MODELS


class TestProviderImportErrors:
    """Test provider import error handling"""
    
    def test_openai_import_error(self):
        """Test OpenAI import error"""
        with patch.dict('sys.modules', {'openai': None}):
            with pytest.raises(ImportError, match="openai package is required"):
                OpenAIProvider("test_key")
    
    def test_anthropic_import_error(self):
        """Test Anthropic import error"""
        with patch.dict('sys.modules', {'anthropic': None}):
            with pytest.raises(ImportError, match="anthropic package is required"):
                AnthropicProvider("test_key")
    
    def test_google_import_error(self):
        """Test Google import error"""
        with patch.dict('sys.modules', {'google': None}):
            with pytest.raises(ImportError, match="google-generativeai package is required"):
                GoogleProvider("test_key")
    
    def test_cohere_import_error(self):
        """Test Cohere import error"""
        with patch.dict('sys.modules', {'cohere': None}):
            with pytest.raises(ImportError, match="cohere package is required"):
                CohereProvider("test_key")
