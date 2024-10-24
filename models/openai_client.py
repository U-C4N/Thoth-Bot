from typing import List, Dict, Any
from openai import OpenAI
from utils.logger import setup_logger
from models.model_config import ModelConfigManager

logger = setup_logger()

class OpenAIClient:
    def __init__(self, config):
        self.config = config
        self.client = OpenAI(api_key=config.get("OpenAI", "api_key"))
        self.default_model = config.get("OpenAI", "default_model")
        self.model_config = ModelConfigManager(config)

    async def get_chat_completion(self, 
                                conversation: List[Dict[str, str]], 
                                model: str = None) -> str:
        """Get chat completion from OpenAI."""
        try:
            model = model or self.default_model
            model_config = self.model_config.get_model_config("openai", model)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=conversation,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                top_p=model_config.top_p,
                presence_penalty=model_config.presence_penalty,
                frequency_penalty=model_config.frequency_penalty,
                stop=model_config.stop_sequences
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI chat completion error: {str(e)}")
            raise

    async def generate_code(self, prompt: str, model: str = None) -> str:
        """Generate code using OpenAI."""
        try:
            model = model or self.default_model
            model_config = self.model_config.get_model_config("openai", model)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a skilled programmer. Generate clean, well-documented code."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                top_p=model_config.top_p,
                presence_penalty=model_config.presence_penalty,
                frequency_penalty=model_config.frequency_penalty,
                stop=model_config.stop_sequences
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI code generation error: {str(e)}")
            raise

    async def get_code_response(self, prompt: str, system_prompt: str, model: str = None) -> str:
        """Generate code with file structure using OpenAI."""
        try:
            model = model or self.default_model
            model_config = self.model_config.get_model_config("openai", model)
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                top_p=model_config.top_p,
                presence_penalty=model_config.presence_penalty,
                frequency_penalty=model_config.frequency_penalty,
                stop=model_config.stop_sequences
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI code response error: {str(e)}")
            raise
