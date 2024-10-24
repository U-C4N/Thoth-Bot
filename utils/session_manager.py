import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from utils.logger import setup_logger

logger = setup_logger()
console = Console()

class SessionManager:
    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = sessions_dir
        os.makedirs(sessions_dir, exist_ok=True)
        
    def save_session(self, conversation: List[Dict[str, str]], name: Optional[str] = None) -> str:
        """Save the current conversation to a file."""
        try:
            if not name:
                name = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            filename = f"{name}.json"
            filepath = os.path.join(self.sessions_dir, filename)
            
            # Ensure unique filename
            counter = 1
            while os.path.exists(filepath):
                filename = f"{name}_{counter}.json"
                filepath = os.path.join(self.sessions_dir, filename)
                counter += 1
            
            session_data = {
                "timestamp": datetime.now().isoformat(),
                "conversation": conversation
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
                
            return filename
            
        except Exception as e:
            logger.error(f"Error saving session: {str(e)}")
            raise
    
    def load_session(self, filename: str) -> List[Dict[str, str]]:
        """Load a conversation from a file."""
        try:
            filepath = os.path.join(self.sessions_dir, filename)
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Session file not found: {filename}")
                
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                
            return session_data.get("conversation", [])
            
        except Exception as e:
            logger.error(f"Error loading session: {str(e)}")
            raise
    
    def list_sessions(self) -> List[Dict[str, str]]:
        """List all available chat sessions."""
        sessions = []
        try:
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.sessions_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        sessions.append({
                            "filename": filename,
                            "timestamp": session_data["timestamp"],
                            "message_count": len(session_data["conversation"])
                        })
            return sorted(sessions, key=lambda x: x["timestamp"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing sessions: {str(e)}")
            raise
    
    def delete_session(self, filename: str) -> bool:
        """Delete a chat session file."""
        try:
            filepath = os.path.join(self.sessions_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            raise
    
    def export_session(self, filename: str, export_format: str = "txt") -> str:
        """Export a chat session to different formats."""
        try:
            session = self.load_session(filename)
            base_name = os.path.splitext(filename)[0]
            export_file = f"{base_name}_export.{export_format}"
            export_path = os.path.join(self.sessions_dir, export_file)
            
            if export_format == "txt":
                with open(export_path, 'w', encoding='utf-8') as f:
                    for msg in session:
                        f.write(f"{msg['role'].upper()}: {msg['content']}\n\n")
            
            elif export_format == "md":
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write("# Chat Session Export\n\n")
                    for msg in session:
                        f.write(f"## {msg['role'].title()}\n\n{msg['content']}\n\n")
            
            return export_file
            
        except Exception as e:
            logger.error(f"Error exporting session: {str(e)}")
            raise
    
    def display_sessions(self) -> None:
        """Display available sessions in a formatted table."""
        try:
            sessions = self.list_sessions()
            
            table = Table(title="Available Chat Sessions")
            table.add_column("Filename", style="cyan")
            table.add_column("Timestamp", style="green")
            table.add_column("Messages", style="yellow")
            
            for session in sessions:
                table.add_row(
                    session["filename"],
                    datetime.fromisoformat(session["timestamp"]).strftime("%Y-%m-%d %H:%M:%S"),
                    str(session["message_count"])
                )
            
            console.print(table)
            
        except Exception as e:
            logger.error(f"Error displaying sessions: {str(e)}")
            raise
