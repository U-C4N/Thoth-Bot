from typing import Optional
import google.generativeai as genai
from utils.logger import setup_logger

logger = setup_logger()

class GeminiClient:
    def __init__(self, config):
        self.config = config
        self.api_key = config.get("Gemini", "api_key")
        self.default_model = config.get("Gemini", "default_model")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name=self.default_model)
        
    async def generate_code(self, prompt: str, model: str = None) -> str:
        """Generate code using Gemini."""
        try:
            model = model or self.default_model
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini code generation error: {str(e)}")
            raise
            
    async def get_code_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate code with file structure using Gemini."""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini code response error: {str(e)}")
            raise
