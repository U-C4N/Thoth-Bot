from utils.config_manager import ConfigManager
from models.model_config import ModelConfigManager
import json

def test_model_configurations():
    config = ConfigManager()
    model_config = ModelConfigManager(config)

    # Test 1: Get available models
    print("Test 1: Getting available models")
    available_models = model_config.get_available_models()
    print(json.dumps(available_models, indent=2))

    # Test 2: Get specific model config
    print("\nTest 2: Getting OpenAI GPT-4 config")
    openai_config = model_config.get_model_config("openai", "gpt-4")
    print("OpenAI GPT-4 config:")
    print(f"- Max tokens: {openai_config.max_tokens}")
    print(f"- Temperature: {openai_config.temperature}")
    print(f"- Top P: {openai_config.top_p}")

    # Test 3: Setting custom config
    print("\nTest 3: Setting custom config")
    openai_config.temperature = 0.8
    openai_config.max_tokens = 2000
    model_config.set_model_config(openai_config)
    
    # Verify the changes
    updated_config = model_config.get_model_config("openai", "gpt-4")
    print("Updated OpenAI GPT-4 config:")
    print(f"- Max tokens: {updated_config.max_tokens}")
    print(f"- Temperature: {updated_config.temperature}")

if __name__ == "__main__":
    test_model_configurations()
