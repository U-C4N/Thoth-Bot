"""Plugin system for AI Assistant."""
from importlib import util
import os
import logging
from typing import Dict, Any, List, Type
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self, config):
        self.config = config
        self.name = self.__class__.__name__
        self.logger = logging.getLogger(self.name)
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin."""
        pass
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute the plugin's main functionality."""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration."""
        return self.config.get_section(f"Plugin.{self.name}")

class PluginManager:
    """Manages plugin discovery, loading, and execution."""
    
    def __init__(self, config):
        self.config = config
        self.plugins: Dict[str, BasePlugin] = {}
        self.logger = logging.getLogger("PluginManager")
        self.plugin_dir = "plugins"
        
    async def discover_plugins(self) -> None:
        """Discover and load available plugins."""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            
        for item in os.listdir(self.plugin_dir):
            if item.endswith('.py') and not item.startswith('__'):
                plugin_name = item[:-3]
                try:
                    await self.load_plugin(plugin_name)
                except Exception as e:
                    self.logger.error(f"Failed to load plugin {plugin_name}: {str(e)}")
    
    async def load_plugin(self, plugin_name: str) -> None:
        """Load a specific plugin by name."""
        try:
            spec = util.spec_from_file_location(
                plugin_name,
                os.path.join(self.plugin_dir, f"{plugin_name}.py")
            )
            if spec and spec.loader:
                module = util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Look for plugin class in module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, BasePlugin) and 
                        attr != BasePlugin):
                        plugin = attr(self.config)
                        if await plugin.initialize():
                            self.plugins[plugin.name] = plugin
                            self.logger.info(f"Successfully loaded plugin: {plugin.name}")
                        break
        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
            raise
    
    def get_plugin(self, name: str) -> BasePlugin:
        """Get a plugin instance by name."""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """List all loaded plugins."""
        return list(self.plugins.keys())
