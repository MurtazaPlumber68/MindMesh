
"""
LLM Service - Abstraction layer for different LLM providers
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import aiohttp
from config.settings import Settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response from messages."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1"
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_text}")


class LocalLLMProvider(LLMProvider):
    """Local LLM provider using transformers."""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.pipeline = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the local model."""
        try:
            from transformers import pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model_name,
                device_map="auto"
            )
        except ImportError:
            raise Exception("transformers package not installed for local LLM")
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using local model."""
        # Convert messages to a single prompt
        prompt = self._messages_to_prompt(messages)
        
        # Run in thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.pipeline(prompt, max_length=500, num_return_sequences=1)
        )
        
        return result[0]["generated_text"]
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert messages format to a single prompt."""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n".join(prompt_parts)


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate mock response."""
        user_message = next((msg["content"] for msg in messages if msg["role"] == "user"), "")
        
        # Simple pattern matching for common requests
        if "list" in user_message.lower():
            return json.dumps({
                "command": "ls -la",
                "explanation": "List all files and directories with detailed information",
                "risk_level": "low",
                "confidence": 0.95,
                "alternatives": ["ls", "ls -l"],
                "warnings": []
            })
        elif "disk" in user_message.lower() and "space" in user_message.lower():
            return json.dumps({
                "command": "df -h",
                "explanation": "Show disk space usage in human-readable format",
                "risk_level": "low",
                "confidence": 0.9,
                "alternatives": ["du -sh", "df"],
                "warnings": []
            })
        else:
            return json.dumps({
                "command": "echo 'Command not recognized'",
                "explanation": "This is a mock response",
                "risk_level": "low",
                "confidence": 0.5,
                "alternatives": [],
                "warnings": ["Mock provider in use"]
            })


class LLMService:
    """Main LLM service that manages different providers."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = self._initialize_provider()
    
    def _initialize_provider(self) -> LLMProvider:
        """Initialize the appropriate LLM provider."""
        provider_type = self.settings.llm_provider.lower()
        
        if provider_type == "openai":
            if not self.settings.openai_api_key:
                print("Warning: No OpenAI API key found, using mock provider")
                return MockLLMProvider()
            return OpenAIProvider(self.settings.openai_api_key, self.settings.openai_model)
        
        elif provider_type == "local":
            try:
                return LocalLLMProvider(self.settings.local_model_name)
            except Exception as e:
                print(f"Warning: Failed to initialize local LLM: {e}, using mock provider")
                return MockLLMProvider()
        
        else:
            print(f"Warning: Unknown provider {provider_type}, using mock provider")
            return MockLLMProvider()
    
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using the configured provider."""
        try:
            return await self.provider.generate_response(messages)
        except Exception as e:
            print(f"LLM Service error: {e}")
            # Fallback to mock provider
            if not isinstance(self.provider, MockLLMProvider):
                mock_provider = MockLLMProvider()
                return await mock_provider.generate_response(messages)
            raise
    
    def switch_provider(self, provider_type: str, **kwargs):
        """Switch to a different LLM provider."""
        if provider_type.lower() == "openai" and "api_key" in kwargs:
            self.provider = OpenAIProvider(kwargs["api_key"], kwargs.get("model", "gpt-4"))
        elif provider_type.lower() == "local":
            self.provider = LocalLLMProvider(kwargs.get("model_name", "microsoft/DialoGPT-medium"))
        elif provider_type.lower() == "mock":
            self.provider = MockLLMProvider()
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
