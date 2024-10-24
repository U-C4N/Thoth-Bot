from typing import List, Dict, Any
from anthropic import Anthropic
from utils.logger import setup_logger
from models.model_config import ModelConfigManager

logger = setup_logger()

class AnthropicClient:
    def __init__(self, config):
        self.config = config
        self.client = Anthropic(api_key=config.get("Anthropic", "api_key"))
        self.default_model = config.get("Anthropic", "default_model")
        self.model_config = ModelConfigManager(config)

    async def get_chat_completion(self, 
                                conversation: List[Dict[str, str]], 
                                model: str = None) -> str:
        """Get chat completion from Anthropic."""
        try:
            model = model or self.default_model
            model_config = self.model_config.get_model_config("anthropic", model)
            
            # Convert conversation history to Anthropic format
            messages = []
            for msg in conversation:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            response = self.client.messages.create(
                model=model,
                messages=messages,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                top_p=model_config.top_p,
                stop_sequences=model_config.stop_sequences
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic chat completion error: {str(e)}")
            raise

    async def generate_code(self, prompt: str, model: str = None) -> str:
        """Generate code using Anthropic."""
        try:
            model = model or self.default_model
            model_config = self.model_config.get_model_config("anthropic", model)
            
            response = self.client.messages.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skilled programmer. Generate clean, well-documented code."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                top_p=model_config.top_p,
                stop_sequences=model_config.stop_sequences
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic code generation error: {str(e)}")
            raise

    async def get_code_response(self, prompt: str, system_prompt: str, model: str = None) -> str:
        """Generate code with file structure using Anthropic."""
        try:
            model = model or self.default_model
            model_config = self.model_config.get_model_config("anthropic", model)
            
            response = self.client.messages.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                top_p=model_config.top_p,
                stop_sequences=model_config.stop_sequences
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic code response error: {str(e)}")
            raise
