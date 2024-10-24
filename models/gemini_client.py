from typing import List, Dict, Any
import google.generativeai as genai
from utils.logger import setup_logger
from models.model_config import ModelConfigManager

logger = setup_logger()

class GeminiClient:
    def __init__(self, config):
        self.config = config
        api_key = config.get("Gemini", "api_key")
        genai.configure(api_key=api_key)
        self.default_model = config.get("Gemini", "default_model")
        self.model = genai.GenerativeModel(self.default_model)
        self.model_config = ModelConfigManager(config)

    async def get_chat_completion(self, 
                                conversation: List[Dict[str, str]], 
                                model: str = None) -> str:
        """Get chat completion from Gemini."""
        try:
            model = model or self.default_model
            model_config = self.model_config.get_model_config("gemini", model)
            
            # Convert conversation history to Gemini format and apply configuration
            chat = self.model.start_chat(
                generation_config={
                    "max_output_tokens": model_config.max_tokens,
                    "temperature": model_config.temperature,
                    "top_p": model_config.top_p,
                    "stop_sequences": model_config.stop_sequences
                }
            )
            
            response = None
            for msg in conversation:
                if msg["role"] == "user":
                    response = chat.send_message(msg["content"])
            
            if response:
                return response.text
            return "No response generated"
            
        except Exception as e:
            logger.error(f"Gemini chat completion error: {str(e)}")
            raise

    async def generate_code(self, prompt: str, model: str = None) -> str:
        """Generate code using Gemini."""
        try:
            model = model or self.default_model
            model_config = self.model_config.get_model_config("gemini", model)
            
            system_prompt = "You are a skilled programmer. Generate clean, well-documented code."
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "max_output_tokens": model_config.max_tokens,
                    "temperature": model_config.temperature,
                    "top_p": model_config.top_p,
                    "stop_sequences": model_config.stop_sequences
                }
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini code generation error: {str(e)}")
            raise

    async def get_code_response(self, prompt: str, system_prompt: str, model: str = None) -> str:
        """Generate code with file structure using Gemini."""
        try:
            model = model or self.default_model
            model_config = self.model_config.get_model_config("gemini", model)
            
            full_prompt = f"{system_prompt}\n\n{prompt}"
            
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    "max_output_tokens": model_config.max_tokens,
                    "temperature": model_config.temperature,
                    "top_p": model_config.top_p,
                    "stop_sequences": model_config.stop_sequences
                }
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini code response error: {str(e)}")
            raise
