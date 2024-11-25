import configparser
import os
from typing import Optional, Dict, Any

class ConfigManager:
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from file or create default if not exists."""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()

    def create_default_config(self) -> None:
        """Create default configuration file."""
        self.config["DEFAULT"] = {
            "log_level": "INFO",
            "log_file": "logs/app.log",
            "ai_provider": "openai"
        }
        self.config["OpenAI"] = {
            "api_key": "your_openai_api_key",
            "default_model": "gpt-4"
        }
        self.config["Anthropic"] = {
            "api_key": "your_anthropic_api_key",
            "default_model": "claude-3-sonnet"
        }
        self.config["Groq"] = {
            "api_key": "your_groq_api_key",
            "default_model": "mixtral-8x7b-32768"
        }
        self.config["Gemini"] = {
            "api_key": "your_gemini_api_key",
            "default_model": "gemini-pro"
        }
        self.config["ArXiv"] = {
            "results_per_page": "10"
        }
        self.save_config()

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            if not self.config_file:
                raise ValueError("No config file specified")
                
            config_dir = os.path.dirname(self.config_file)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
                
            with open(self.config_file, "w") as f:
                self.config.write(f)
        except Exception as e:
            raise RuntimeError(f"Failed to save configuration: {str(e)}")

    def get(self, section: str, key: str, fallback: Any = None) -> Any:
        """Get configuration value."""
        try:
            if section == "DEFAULT":
                return self.config.defaults().get(key, fallback)
            return self.config.get(section, key, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback

    def set(self, section: str, key: str, value: str) -> None:
        """Set configuration value."""
        if not section:
            raise ValueError("Section name cannot be empty")
            
        if section != "DEFAULT" and not self.config.has_section(section):
            self.config.add_section(section)
        self.config[section][key] = value
        self.save_config()

    def get_section(self, section: str) -> Dict[str, str]:
        """Get all key-value pairs in a section."""
        if not self.config.has_section(section):
            return {}
        return dict(self.config[section])
