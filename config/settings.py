
"""
Settings and configuration management
"""

import os
from typing import Optional
from pathlib import Path


class Settings:
    """Application settings and configuration."""
    
    def __init__(self):
        # LLM Configuration
        self.llm_provider = os.getenv("RLLM_PROVIDER", "mock")  # openai, local, mock
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.local_model_name = os.getenv("LOCAL_MODEL", "microsoft/DialoGPT-medium")
        
        # Database Configuration
        self.database_path = os.getenv("RLLM_DB_PATH", "~/.rllm/commands.db")
        
        # Safety Configuration
        self.safety_level = os.getenv("RLLM_SAFETY_LEVEL", "medium")  # low, medium, high, strict
        self.require_confirmation = os.getenv("RLLM_REQUIRE_CONFIRMATION", "true").lower() == "true"
        
        # Context Configuration
        self.max_context_history = int(os.getenv("RLLM_MAX_CONTEXT", "50"))
        self.max_query_length = int(os.getenv("RLLM_MAX_QUERY_LENGTH", "500"))
        
        # Output Configuration
        self.output_format = os.getenv("RLLM_OUTPUT_FORMAT", "rich")  # plain, rich
        self.show_explanations = os.getenv("RLLM_SHOW_EXPLANATIONS", "true").lower() == "true"
        self.show_alternatives = os.getenv("RLLM_SHOW_ALTERNATIVES", "true").lower() == "true"
        
        # Performance Configuration
        self.request_timeout = int(os.getenv("RLLM_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("RLLM_MAX_RETRIES", "3"))
        
        # Create config directory if it doesn't exist
        self.config_dir = Path("~/.rllm").expanduser()
        self.config_dir.mkdir(exist_ok=True)
    
    def validate(self) -> bool:
        """Validate current settings."""
        issues = []
        
        # Check LLM provider configuration
        if self.llm_provider == "openai" and not self.openai_api_key:
            issues.append("OpenAI API key is required when using OpenAI provider")
        
        # Check safety level
        if self.safety_level not in ["low", "medium", "high", "strict"]:
            issues.append(f"Invalid safety level: {self.safety_level}")
        
        # Check numeric values
        if self.max_context_history < 1:
            issues.append("max_context_history must be positive")
        
        if self.max_query_length < 10:
            issues.append("max_query_length must be at least 10")
        
        if issues:
            print("Configuration issues found:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        return True
    
    def save_config(self, config_file: Optional[str] = None):
        """Save current settings to configuration file."""
        if not config_file:
            config_file = self.config_dir / "config.env"
        
        config_lines = [
            f"RLLM_PROVIDER={self.llm_provider}",
            f"OPENAI_MODEL={self.openai_model}",
            f"LOCAL_MODEL={self.local_model_name}",
            f"RLLM_DB_PATH={self.database_path}",
            f"RLLM_SAFETY_LEVEL={self.safety_level}",
            f"RLLM_REQUIRE_CONFIRMATION={str(self.require_confirmation).lower()}",
            f"RLLM_MAX_CONTEXT={self.max_context_history}",
            f"RLLM_MAX_QUERY_LENGTH={self.max_query_length}",
            f"RLLM_OUTPUT_FORMAT={self.output_format}",
            f"RLLM_SHOW_EXPLANATIONS={str(self.show_explanations).lower()}",
            f"RLLM_SHOW_ALTERNATIVES={str(self.show_alternatives).lower()}",
            f"RLLM_TIMEOUT={self.request_timeout}",
            f"RLLM_MAX_RETRIES={self.max_retries}"
        ]
        
        with open(config_file, 'w') as f:
            f.write('\n'.join(config_lines))
    
    def load_config(self, config_file: Optional[str] = None):
        """Load settings from configuration file."""
        if not config_file:
            config_file = self.config_dir / "config.env"
        
        if not Path(config_file).exists():
            return
        
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        
        # Reload settings from environment
        self.__init__()
    
    def get_config_summary(self) -> dict:
        """Get a summary of current configuration."""
        return {
            'llm_provider': self.llm_provider,
            'openai_model': self.openai_model,
            'safety_level': self.safety_level,
            'max_context_history': self.max_context_history,
            'output_format': self.output_format,
            'config_dir': str(self.config_dir),
            'database_path': self.database_path
        }
