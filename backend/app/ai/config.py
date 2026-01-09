"""AI API key detection and configuration"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

from ..config import BASE_DIR


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"  # Gemini
    COHERE = "cohere"
    # Add more providers as needed
    # MISTRAL = "mistral"
    # PERPLEXITY = "perplexity"


class AIConfig:
    """Manages AI API configuration"""
    
    # Environment variable patterns for each provider
    PROVIDER_ENV_PATTERNS = {
        AIProvider.OPENAI: [
            r"OPENAI_API_KEY",
            r"OPENAI_KEY",
            r"GPT.*API.*KEY",
        ],
        AIProvider.ANTHROPIC: [
            r"ANTHROPIC_API_KEY",
            r"ANTHROPIC_KEY",
            r"CLAUDE.*API.*KEY",
        ],
        AIProvider.GOOGLE: [
            r"GOOGLE_API_KEY",
            r"GEMINI_API_KEY",
            r"GOOGLE.*API.*KEY",
            r"GEMINI.*API.*KEY",
        ],
        AIProvider.COHERE: [
            r"COHERE_API_KEY",
            r"COHERE_KEY",
        ],
    }
    
    # Shell config file locations
    SHELL_CONFIG_FILES = [
        ".bashrc",
        ".bashrc.local",
        ".zshrc",
        ".zshrc.local",
        ".profile",
        ".bash_profile",
    ]
    
    @classmethod
    def detect_api_keys(cls) -> Dict[AIProvider, List[Tuple[str, str]]]:
        """
        Detect API keys from all possible sources
        
        Returns:
            Dictionary mapping providers to list of (source, key) tuples
        """
        detected = {}
        
        # Check .env files first (project-specific, highest priority)
        env_keys = cls._detect_from_env_files()
        for provider, keys in env_keys.items():
            if provider not in detected:
                detected[provider] = []
            detected[provider].extend(keys)
        
        # Check environment variables
        env_var_keys = cls._detect_from_environment()
        for provider, keys in env_var_keys.items():
            if provider not in detected:
                detected[provider] = []
            detected[provider].extend(keys)
        
        # Check shell config files
        shell_keys = cls._detect_from_shell_configs()
        for provider, keys in shell_keys.items():
            if provider not in detected:
                detected[provider] = []
            detected[provider].extend(keys)
        
        return detected
    
    @classmethod
    def _detect_from_env_files(cls) -> Dict[AIProvider, List[Tuple[str, str]]]:
        """Detect API keys from .env files"""
        detected = {}
        env_files = [
            BASE_DIR / ".env.local",
            BASE_DIR / ".env",
        ]
        
        for env_file in env_files:
            if not env_file.exists():
                continue
            
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    for provider, patterns in cls.PROVIDER_ENV_PATTERNS.items():
                        for pattern in patterns:
                            # Look for KEY=value patterns
                            regex = re.compile(
                                rf'^{pattern}\s*=\s*["\']?([^"\'\n]+)["\']?',
                                re.IGNORECASE | re.MULTILINE
                            )
                            matches = regex.findall(content)
                            for key in matches:
                                if provider not in detected:
                                    detected[provider] = []
                                detected[provider].append((f"env:{env_file.name}", key.strip()))
            except Exception:
                continue
        
        return detected
    
    @classmethod
    def _detect_from_environment(cls) -> Dict[AIProvider, List[Tuple[str, str]]]:
        """Detect API keys from environment variables"""
        detected = {}
        
        for provider, patterns in cls.PROVIDER_ENV_PATTERNS.items():
            for pattern in patterns:
                # Try exact match first
                key = os.getenv(pattern)
                if key:
                    if provider not in detected:
                        detected[provider] = []
                    detected[provider].append((f"env_var:{pattern}", key))
                
                # Try case-insensitive match
                for env_key, env_value in os.environ.items():
                    if re.match(pattern, env_key, re.IGNORECASE):
                        if provider not in detected:
                            detected[provider] = []
                        detected[provider].append((f"env_var:{env_key}", env_value))
                        break
        
        return detected
    
    @classmethod
    def _detect_from_shell_configs(cls) -> Dict[AIProvider, List[Tuple[str, str]]]:
        """Detect API keys from shell configuration files"""
        detected = {}
        home = Path.home()
        
        for config_file in cls.SHELL_CONFIG_FILES:
            config_path = home / config_file
            if not config_path.exists():
                continue
            
            try:
                with open(config_path, 'r') as f:
                    content = f.read()
                    for provider, patterns in cls.PROVIDER_ENV_PATTERNS.items():
                        for pattern in patterns:
                            # Look for export KEY=value patterns
                            regex = re.compile(
                                rf'export\s+{pattern}\s*=\s*["\']?([^"\'\n]+)["\']?',
                                re.IGNORECASE | re.MULTILINE
                            )
                            matches = regex.findall(content)
                            for key in matches:
                                if provider not in detected:
                                    detected[provider] = []
                                detected[provider].append((f"shell:{config_file}", key.strip()))
            except Exception:
                continue
        
        return detected
    
    @classmethod
    def get_available_providers(cls) -> List[AIProvider]:
        """Get list of providers with detected API keys"""
        detected = cls.detect_api_keys()
        return [provider for provider, keys in detected.items() if keys]
    
    @classmethod
    def get_api_key(cls, provider: AIProvider, source_preference: Optional[List[str]] = None) -> Optional[str]:
        """
        Get API key for a provider with optional source preference
        
        Args:
            provider: The AI provider
            source_preference: List of preferred sources (e.g., ["env:.env.local", "env_var:OPENAI_API_KEY"])
            
        Returns:
            API key if found, None otherwise
        """
        detected = cls.detect_api_keys()
        
        if provider not in detected or not detected[provider]:
            return None
        
        keys = detected[provider]
        
        # If source preference is specified, try those first
        if source_preference:
            for preferred_source in source_preference:
                for source, key in keys:
                    if source.startswith(preferred_source):
                        return key
        
        # Otherwise, return the first key found (prioritized by detection order)
        return keys[0][1] if keys else None


# Convenience functions
def detect_api_keys() -> Dict[AIProvider, List[Tuple[str, str]]]:
    """Detect API keys from all sources"""
    return AIConfig.detect_api_keys()


def get_available_providers() -> List[AIProvider]:
    """Get list of available providers"""
    return AIConfig.get_available_providers()
