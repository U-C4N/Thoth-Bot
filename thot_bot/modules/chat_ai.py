import asyncio
from groq import AsyncGroq
from rich.console import Console
from rich.panel import Panel

console = Console()

class ChatAI:
    def __init__(self, config, api_manager):
        self.config = config
        self.api_manager = api_manager
        self.client = AsyncGroq(api_key=self.config.groq_api_key)
        self.model = None
        self.chat_history = []
    
    async def run(self):
        console.print(Panel("Welcome to Chat AI!", title="Chat AI", expand=False))
        self.model = await self.select_model()
        console.print(f"Selected model: {self.model}")

        while True:
            user_input = await self.get_user_input("You: ")
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == '/clear':
                self.clear_chat()
                continue
            elif user_input.lower() == '/ret':
                console.print("Returning to main menu...")
                return

            response = await self.get_model_response(user_input)
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": response})
            self.display_chat()

    async def get_model_response(self, prompt):
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=self.chat_history + [{"role": "user", "content": prompt}],
                model=self.model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"An error occurred: {str(e)}"

    async def select_model(self):
        console.print("Available models:")
        console.print("1. gemma2-9b-it")
        console.print("2. gemma-7b-it")
        console.print("3. llama-3.1-70b-versatile")
        while True:
            choice = await self.get_user_input("Select a model (1-3): ")
            if choice == '1':
                return "gemma2-9b-it"
            elif choice == '2':
                return "gemma-7b-it"
            elif choice == '3':
                return "llama-3.1-70b-versatile"
            else:
                console.print("Invalid choice. Please try again.", style="bold red")

    async def get_user_input(self, prompt):
        return await asyncio.get_event_loop().run_in_executor(None, input, prompt)

    def clear_chat(self):
        self.chat_history = []
        console.clear()
        console.print(Panel("Chat history cleared.", title="Chat AI", expand=False))

    def display_chat(self):
        console.clear()
        for message in self.chat_history:
            if message["role"] == "user":
                console.print(Panel(message["content"], title="You", style="bold green", expand=False))
            else:
                console.print(Panel(message["content"], title="AI", style="bold blue", expand=False))
        console.print("\nType '/clear' to clear chat history, '/ret' to return to main menu, or 'exit' to quit Chat AI.")