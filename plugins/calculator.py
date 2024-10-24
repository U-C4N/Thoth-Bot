"""Example calculator plugin."""
from typing import Dict, Any
from plugins import BasePlugin

class CalculatorPlugin(BasePlugin):
    """A simple calculator plugin."""
    
    async def initialize(self) -> bool:
        """Initialize the calculator plugin."""
        try:
            # Get plugin configuration or set defaults
            config = self.get_config()
            self.precision = int(config.get('precision', '2'))
            self.max_value = float(config.get('max_value', '1e10'))
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize calculator plugin: {str(e)}")
            return False
    
    async def execute(self, operation: str = None, *numbers: float) -> Dict[str, Any]:
        """Execute calculator operations."""
        try:
            if not operation:
                return {
                    "status": "error",
                    "message": "Operation required. Available operations: add, subtract, multiply, divide",
                    "example": "Use: operation='add', numbers=[1, 2, 3]"
                }
                
            if not numbers:
                return {
                    "status": "error",
                    "message": "Numbers required",
                    "example": "Example: operation='add', numbers=[1, 2, 3]"
                }
                
            if operation == "add":
                result = sum(numbers)
            elif operation == "multiply":
                result = 1
                for num in numbers:
                    result *= num
            elif operation == "subtract":
                result = numbers[0] - sum(numbers[1:])
            elif operation == "divide":
                result = numbers[0]
                for num in numbers[1:]:
                    if num == 0:
                        raise ValueError("Division by zero")
                    result /= num
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            if abs(result) > self.max_value:
                raise ValueError("Result exceeds maximum allowed value")
                
            return {
                "status": "success",
                "operation": operation,
                "numbers": numbers,
                "result": round(result, self.precision)
            }
            
        except Exception as e:
            self.logger.error(f"Calculator error: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
