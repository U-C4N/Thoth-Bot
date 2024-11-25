from typing import Dict, Any, Optional, List
from pydantic import BaseModel

class ModelConfig(BaseModel):
    """Configuration for an AI model."""
    name: str
    provider: str
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    context_window: Optional[int] = None
    stop_sequences: Optional[List[str]] = None

    model_config = {
        "from_attributes": True,
        "validate_assignment": True,
        "extra": "allow",
        "str_strip_whitespace": True,
        "validate_default": True,
        "json_schema_extra": {
            "example": {
                "name": "gpt-4",
                "provider": "openai",
                "max_tokens": 4096,
                "temperature": 0.7
            }
        }
    }

class ModelConfigManager:
    """Manages AI model configurations."""
    def __init__(self, config):
        self.config_manager = config
        self.default_configs = {
            "openai": {
                "gpt-4": ModelConfig(
                    name="gpt-4",
                    provider="openai",
                    max_tokens=4096,
                    context_window=8192
                ),
                "gpt-4-turbo": ModelConfig(
                    name="gpt-4-turbo",
                    provider="openai",
                    max_tokens=4096,
                    context_window=128000
                )
            },
            "anthropic": {
                "claude-3-opus": ModelConfig(
                    name="claude-3-opus",
                    provider="anthropic",
                    max_tokens=4096,
                    context_window=200000
                ),
                "claude-3-sonnet": ModelConfig(
                    name="claude-3-sonnet",
                    provider="anthropic",
                    max_tokens=4096,
                    context_window=200000
                )
            },
            "groq": {
                "mixtral-8x7b-32768": ModelConfig(
                    name="mixtral-8x7b-32768",
                    provider="groq",
                    max_tokens=4096,
                    context_window=32768
                )
            },
            "gemini": {
                "gemini-pro": ModelConfig(
                    name="gemini-pro",
                    provider="gemini",
                    max_tokens=4096,
                    context_window=32768
                )
            }
        }

    def get_model_config(self, provider: str, model_name: str) -> ModelConfig:
        """Get model configuration."""
        try:
            section = f"Models.{provider}.{model_name}"
            if self.config_manager.config.has_section(section):
                config_dict = self.config_manager.get_section(section)
                return ModelConfig(
                    name=model_name,
                    provider=provider,
                    max_tokens=int(config_dict.get('max_tokens', 4096)),
                    temperature=float(config_dict.get('temperature', 0.7)),
                    top_p=float(config_dict.get('top_p', 1.0)),
                    presence_penalty=float(config_dict.get('presence_penalty', 0.0)),
                    frequency_penalty=float(config_dict.get('frequency_penalty', 0.0)),
                    context_window=int(config_dict.get('context_window', 0)) or None,
                    stop_sequences=config_dict.get('stop_sequences', '').split(',') if config_dict.get('stop_sequences') else None
                )
            return self.default_configs[provider][model_name]
        except KeyError:
            raise ValueError(f"No configuration found for {provider} model: {model_name}")

    def set_model_config(self, config: ModelConfig) -> None:
        """Save model configuration."""
        section = f"Models.{config.provider}.{config.name}"
        if not self.config_manager.config.has_section(section):
            self.config_manager.config.add_section(section)
            
        self.config_manager.set(section, 'max_tokens', str(config.max_tokens or ''))
        self.config_manager.set(section, 'temperature', str(config.temperature))
        self.config_manager.set(section, 'top_p', str(config.top_p))
        self.config_manager.set(section, 'presence_penalty', str(config.presence_penalty))
        self.config_manager.set(section, 'frequency_penalty', str(config.frequency_penalty))
        self.config_manager.set(section, 'context_window', str(config.context_window or ''))
        if config.stop_sequences:
            self.config_manager.set(section, 'stop_sequences', ','.join(config.stop_sequences))

    def get_available_models(self, provider: str = None) -> Dict[str, list]:
        """Get available models, optionally filtered by provider."""
        if provider:
            return {provider: list(self.default_configs.get(provider, {}).keys())}
        return {p: list(models.keys()) for p, models in self.default_configs.items()}
