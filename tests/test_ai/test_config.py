"""Tests for AI configuration and API key detection"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from backend.app.ai.config import AIConfig, AIProvider, detect_api_keys, get_available_providers


class TestAIConfig:
    """Test AI configuration and API key detection"""
    
    def test_detect_from_env_variables(self):
        """Test detection from environment variables"""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test_openai_key",
            "ANTHROPIC_API_KEY": "test_anthropic_key",
            "GOOGLE_API_KEY": "test_google_key",
            "COHERE_API_KEY": "test_cohere_key",
        }):
            detected = AIConfig.detect_api_keys()
            
            assert AIProvider.OPENAI in detected
            assert AIProvider.ANTHROPIC in detected
            assert AIProvider.GOOGLE in detected
            assert AIProvider.COHERE in detected
            
            # Check that keys are found
            assert len(detected[AIProvider.OPENAI]) > 0
            assert len(detected[AIProvider.ANTHROPIC]) > 0
    
    def test_detect_from_env_file(self):
        """Test detection from .env file"""
        env_content = """
OPENAI_API_KEY=test_openai_key
ANTHROPIC_API_KEY=test_anthropic_key
GOOGLE_API_KEY=test_google_key
COHERE_API_KEY=test_cohere_key
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_path = Path(f.name)
        
        try:
            with patch('backend.app.ai.config.BASE_DIR', env_path.parent):
                # Mock the .env file location
                with patch('pathlib.Path.exists', return_value=True):
                    with patch('builtins.open', mock_open(read_data=env_content)):
                        detected = AIConfig._detect_from_env_files()
                        
                        assert AIProvider.OPENAI in detected
                        assert AIProvider.ANTHROPIC in detected
        finally:
            env_path.unlink()
    
    def test_detect_from_shell_config(self):
        """Test detection from shell config files"""
        shell_content = """
export OPENAI_API_KEY=test_openai_key
export ANTHROPIC_API_KEY=test_anthropic_key
export GOOGLE_API_KEY=test_google_key
"""
        with patch('pathlib.Path.home', return_value=Path('/tmp')):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', mock_open(read_data=shell_content)):
                    detected = AIConfig._detect_from_shell_configs()
                    
                    assert AIProvider.OPENAI in detected
                    assert AIProvider.ANTHROPIC in detected
    
    def test_get_api_key_with_preference(self):
        """Test getting API key with source preference"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env_key"}):
            # Mock env file detection
            with patch.object(AIConfig, '_detect_from_env_files', return_value={
                AIProvider.OPENAI: [("env:.env.local", "local_key")]
            }):
                # Prefer env file
                key = AIConfig.get_api_key(
                    AIProvider.OPENAI,
                    source_preference=["env:.env.local"]
                )
                assert key == "local_key"
    
    def test_get_available_providers(self):
        """Test getting list of available providers"""
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test_key",
            "ANTHROPIC_API_KEY": "test_key",
        }):
            providers = get_available_providers()
            
            assert AIProvider.OPENAI in providers
            assert AIProvider.ANTHROPIC in providers
    
    def test_provider_enum_values(self):
        """Test that all expected providers are defined"""
        assert AIProvider.OPENAI.value == "openai"
        assert AIProvider.ANTHROPIC.value == "anthropic"
        assert AIProvider.GOOGLE.value == "google"
        assert AIProvider.COHERE.value == "cohere"
