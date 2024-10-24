import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.markdown import Markdown
from utils.logger import setup_logger

logger = setup_logger()
console = Console()

class ExportManager:
    """Manages exports for various features including search results and conversations."""
    
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = export_dir
        self._ensure_export_directories()
    
    def _ensure_export_directories(self) -> None:
        """Ensure all required export directories exist."""
        directories = [
            self.export_dir,
            os.path.join(self.export_dir, "conversations"),
            os.path.join(self.export_dir, "web_search"),
            os.path.join(self.export_dir, "arxiv_search")
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def _generate_filename(self, base_name: str, export_format: str) -> str:
        """Generate a unique filename for the export."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{base_name}_{timestamp}.{export_format}"
    
    def export_search_results(self, 
                            results: List[Dict[str, Any]], 
                            search_type: str,
                            query: str,
                            export_format: str = "md") -> str:
        """Export search results to a file."""
        try:
            # Determine export directory based on search type
            if search_type == "web":
                subdir = "web_search"
            elif search_type == "arxiv":
                subdir = "arxiv_search"
            else:
                raise ValueError(f"Invalid search type: {search_type}")
            
            export_path = os.path.join(self.export_dir, subdir)
            filename = self._generate_filename(f"{search_type}_search", export_format)
            filepath = os.path.join(export_path, filename)
            
            if export_format == "md":
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"# {search_type.title()} Search Results\n\n")
                    f.write(f"**Query:** {query}\n\n")
                    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    for i, result in enumerate(results, 1):
                        f.write(f"## Result {i}\n\n")
                        if search_type == "web":
                            f.write(f"**Title:** {result.get('title', 'N/A')}\n\n")
                            f.write(f"**URL:** {result.get('url', 'N/A')}\n\n")
                            f.write(f"**Summary:** {result.get('summary', 'N/A')}\n\n")
                        elif search_type == "arxiv":
                            f.write(f"**Title:** {result.get('title', 'N/A')}\n\n")
                            f.write(f"**Authors:** {', '.join(result.get('authors', []))}\n\n")
                            f.write(f"**Abstract:** {result.get('abstract', 'N/A')}\n\n")
                            f.write(f"**URL:** {result.get('url', 'N/A')}\n\n")
            
            elif export_format == "json":
                export_data = {
                    "type": search_type,
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "results": results
                }
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            elif export_format == "txt":
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"{search_type.upper()} SEARCH RESULTS\n\n")
                    f.write(f"Query: {query}\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    for i, result in enumerate(results, 1):
                        f.write(f"Result {i}:\n")
                        if search_type == "web":
                            f.write(f"Title: {result.get('title', 'N/A')}\n")
                            f.write(f"URL: {result.get('url', 'N/A')}\n")
                            f.write(f"Summary: {result.get('summary', 'N/A')}\n")
                        elif search_type == "arxiv":
                            f.write(f"Title: {result.get('title', 'N/A')}\n")
                            f.write(f"Authors: {', '.join(result.get('authors', []))}\n")
                            f.write(f"Abstract: {result.get('abstract', 'N/A')}\n")
                            f.write(f"URL: {result.get('url', 'N/A')}\n")
                        f.write("\n")
            
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
            return filename
        
        except Exception as e:
            logger.error(f"Error exporting search results: {str(e)}")
            raise

    def export_conversation(self, 
                          conversation: List[Dict[str, str]], 
                          export_format: str = "md",
                          name: Optional[str] = None) -> str:
        """Enhanced version of conversation export with better formatting."""
        try:
            export_path = os.path.join(self.export_dir, "conversations")
            base_name = name or "conversation"
            filename = self._generate_filename(base_name, export_format)
            filepath = os.path.join(export_path, filename)
            
            if export_format == "md":
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("# AI Assistant Conversation\n\n")
                    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    for msg in conversation:
                        role = msg['role'].title()
                        content = msg['content']
                        f.write(f"## {role}\n\n{content}\n\n")
                        f.write("---\n\n")  # Add separator between messages
            
            elif export_format == "json":
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "conversation": conversation
                }
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            elif export_format == "txt":
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("AI Assistant Conversation\n")
                    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    for msg in conversation:
                        f.write(f"{msg['role'].upper()}:\n")
                        f.write(f"{msg['content']}\n")
                        f.write("\n" + "="*50 + "\n\n")  # Add clear separator
            
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
            
            return filename
        
        except Exception as e:
            logger.error(f"Error exporting conversation: {str(e)}")
            raise
