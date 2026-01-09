"""Tests for AI client"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from backend.app.ai.client import AIClient
from backend.app.ai.config import AIProvider
from backend.app.ai.providers import BaseAIProvider


class TestAIClient:
    """Test AI client functionality"""
    
    def test_init_with_auto_detection(self, db_session):
        """Test client initialization with auto-detection"""
        with patch('backend.app.ai.client.get_available_providers', return_value=[AIProvider.OPENAI]):
            with patch('backend.app.ai.client.AIConfig.get_api_key', return_value="test_key"):
                with patch('backend.app.ai.client.get_provider') as mock_get_provider:
                    mock_provider = Mock(spec=BaseAIProvider)
                    mock_get_provider.return_value = mock_provider
                    
                    client = AIClient(db_session)
                    
                    assert client.provider == AIProvider.OPENAI
                    assert client.ai_provider == mock_provider
    
    def test_init_with_specific_provider(self, db_session):
        """Test client initialization with specific provider"""
        with patch('backend.app.ai.client.AIConfig.get_api_key', return_value="test_key"):
            with patch('backend.app.ai.client.get_provider') as mock_get_provider:
                mock_provider = Mock(spec=BaseAIProvider)
                mock_get_provider.return_value = mock_provider
                
                client = AIClient(db_session, provider=AIProvider.ANTHROPIC)
                
                assert client.provider == AIProvider.ANTHROPIC
                mock_get_provider.assert_called_with(AIProvider.ANTHROPIC, "test_key", model=None)
    
    def test_init_with_custom_model(self, db_session):
        """Test client initialization with custom model"""
        with patch('backend.app.ai.client.AIConfig.get_api_key', return_value="test_key"):
            with patch('backend.app.ai.client.get_provider') as mock_get_provider:
                mock_provider = Mock(spec=BaseAIProvider)
                mock_get_provider.return_value = mock_provider
                
                client = AIClient(db_session, provider=AIProvider.OPENAI, model="gpt-4o")
                
                mock_get_provider.assert_called_with(AIProvider.OPENAI, "test_key", model="gpt-4o")
    
    def test_init_no_providers_found(self, db_session):
        """Test error when no providers are found"""
        with patch('backend.app.ai.client.get_available_providers', return_value=[]):
            with pytest.raises(ValueError, match="No AI providers found"):
                AIClient(db_session)
    
    def test_init_no_api_key(self, db_session):
        """Test error when no API key is found"""
        with patch('backend.app.ai.client.get_available_providers', return_value=[AIProvider.OPENAI]):
            with patch('backend.app.ai.client.AIConfig.get_api_key', return_value=None):
                with pytest.raises(ValueError, match="No API key found"):
                    AIClient(db_session)
    
    def test_query_with_intelligent_selection(self, db_session):
        """Test query with intelligent data selection"""
        mock_provider = Mock(spec=BaseAIProvider)
        mock_provider.query.return_value = "Test response"
        
        with patch('backend.app.ai.client.get_available_providers', return_value=[AIProvider.OPENAI]):
            with patch('backend.app.ai.client.AIConfig.get_api_key', return_value="test_key"):
                with patch('backend.app.ai.client.get_provider', return_value=mock_provider):
                    client = AIClient(db_session)
                    
                    result = client.query("how much did I spend")
                    
                    assert result["response"] == "Test response"
                    assert result["provider"] == "openai"
                    assert "data_included" in result
                    mock_provider.query.assert_called_once()
    
    def test_query_with_full_data(self, db_session):
        """Test query with full data export"""
        mock_provider = Mock(spec=BaseAIProvider)
        mock_provider.query.return_value = "Test response"
        
        with patch('backend.app.ai.client.get_available_providers', return_value=[AIProvider.OPENAI]):
            with patch('backend.app.ai.client.AIConfig.get_api_key', return_value="test_key"):
                with patch('backend.app.ai.client.get_provider', return_value=mock_provider):
                    with patch('backend.app.ai.client.export_accounts') as mock_export:
                        mock_export.return_value = []
                        
                        client = AIClient(db_session)
                        result = client.query("comprehensive analysis", include_full_data=True)
                        
                        assert result["response"] == "Test response"
                        # Should call with full export data
                        call_args = mock_provider.query.call_args
                        assert call_args is not None
    
    def test_query_error_handling(self, db_session):
        """Test error handling in query"""
        mock_provider = Mock(spec=BaseAIProvider)
        mock_provider.query.side_effect = Exception("API Error")
        
        with patch('backend.app.ai.client.get_available_providers', return_value=[AIProvider.OPENAI]):
            with patch('backend.app.ai.client.AIConfig.get_api_key', return_value="test_key"):
                with patch('backend.app.ai.client.get_provider', return_value=mock_provider):
                    client = AIClient(db_session)
                    
                    result = client.query("test query")
                    
                    assert "error" in result
                    assert result["error"] == "API Error"
    
    def test_get_available_providers_class_method(self, db_session):
        """Test class method to get available providers"""
        with patch('backend.app.ai.client.get_available_providers', return_value=[AIProvider.OPENAI, AIProvider.ANTHROPIC]):
            providers = AIClient.get_available_providers()
            
            assert AIProvider.OPENAI in providers
            assert AIProvider.ANTHROPIC in providers
    
    def test_list_providers_with_keys(self, db_session):
        """Test listing providers with their API key sources"""
        mock_detected = {
            AIProvider.OPENAI: [("env_var:OPENAI_API_KEY", "test_key")],
            AIProvider.ANTHROPIC: [("env:.env.local", "test_key2")],
        }
        
        with patch('backend.app.ai.client.AIConfig.detect_api_keys', return_value=mock_detected):
            providers = AIClient.list_providers_with_keys()
            
            assert AIProvider.OPENAI in providers
            assert AIProvider.ANTHROPIC in providers
            assert len(providers[AIProvider.OPENAI]) > 0
