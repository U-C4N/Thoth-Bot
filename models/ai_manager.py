from typing import List, Dict, Any, Optional
from .openai_client import OpenAIClient
from .anthropic_client import AnthropicClient
from .groq_client import GroqClient
from .gemini_client import GeminiClient
from utils.logger import setup_logger

logger = setup_logger()

class AIManager:
    def __init__(self, config):
        self.config = config
        self.openai = OpenAIClient(config)
        self.anthropic = AnthropicClient(config)
        self.groq = GroqClient(config)
        self.gemini = GeminiClient(config)
        self.default_provider = config.get("DEFAULT", "ai_provider", fallback="openai")

    async def get_chat_response(self, 
                              conversation: List[Dict[str, str]], 
                              provider: Optional[str] = None) -> str:
        """Get response from the selected AI provider."""
        provider = provider or self.default_provider
        
        try:
            if provider == "openai":
                return await self.openai.get_chat_completion(conversation)
            elif provider == "anthropic":
                return await self.anthropic.get_chat_completion(conversation)
            elif provider == "groq":
                return await self.groq.get_chat_completion(conversation)
            elif provider == "gemini":
                return await self.gemini.get_chat_completion(conversation)
            else:
                raise ValueError(f"Unknown AI provider: {provider}")
        except Exception as e:
            logger.error(f"Error getting chat response: {str(e)}")
            raise

    async def generate_code(self, 
                          prompt: str,
                          provider: Optional[str] = None) -> str:
        """Generate code using the selected AI provider."""
        provider = provider or self.default_provider
        
        try:
            if provider == "openai":
                return await self.openai.generate_code(prompt)
            elif provider == "anthropic":
                return await self.anthropic.generate_code(prompt)
            elif provider == "groq":
                return await self.groq.generate_code(prompt)
            elif provider == "gemini":
                return await self.gemini.generate_code(prompt)
            else:
                raise ValueError(f"Unknown AI provider: {provider}")
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            raise

    async def get_code_response(self, prompt: str, provider: Optional[str] = None) -> str:
        """Get code generation response with file structure from the selected AI provider."""
        provider = provider or self.default_provider
        
        try:
            system_prompt = """You are a Python code generation assistant. When generating code:
            1. Create a complete Python project structure
            2. Format your response with FOLDER: and FILE: prefixes
            3. Include all necessary files and their contents
            4. Ensure code is complete and properly formatted
            5. Use Python best practices and common project structures
            6. Include requirements.txt or setup.py when needed
            7. Add appropriate .gitignore file
            8. Include README.md with setup and usage instructions
            
            Example format:
            FOLDER: src/
            FOLDER: src/utils/
            FOLDER: tests/
            FILE: requirements.txt
            flask==2.0.1
            pytest==6.2.5
            
            FILE: src/__init__.py
            # Package initialization
            
            FILE: src/main.py
            from flask import Flask
            # Python code here...
            
            FILE: README.md
            # Project Name
            Setup and usage instructions...
            """

            if provider == "openai":
                return await self.openai.get_code_response(prompt, system_prompt)
            elif provider == "anthropic":
                return await self.anthropic.get_code_response(prompt, system_prompt)
            elif provider == "groq":
                return await self.groq.get_code_response(prompt, system_prompt)
            elif provider == "gemini":
                return await self.gemini.get_code_response(prompt, system_prompt)
            else:
                raise ValueError(f"Unknown AI provider: {provider}")
        except Exception as e:
            logger.error(f"Error getting code response: {str(e)}")
            raise
