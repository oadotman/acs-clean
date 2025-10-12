"""
Tool registry for discovering and managing available tools
"""

import importlib
from typing import Dict, List, Optional, Type, Any
from .core import ToolRunner, ToolConfig, ToolType
from .exceptions import ToolError, ToolConfigError


class ToolRegistry:
    """Registry for managing available tools"""
    
    def __init__(self):
        self._tools: Dict[str, Type[ToolRunner]] = {}
        self._configs: Dict[str, ToolConfig] = {}
        self._instances: Dict[str, ToolRunner] = {}
    
    def register_tool(
        self, 
        tool_class: Type[ToolRunner], 
        config: ToolConfig,
        replace_existing: bool = False
    ):
        """
        Register a tool class with configuration
        
        Args:
            tool_class: ToolRunner subclass
            config: Tool configuration
            replace_existing: Whether to replace existing registration
        """
        tool_name = config.name
        
        if tool_name in self._tools and not replace_existing:
            raise ToolConfigError(
                tool_name, 
                f"Tool '{tool_name}' already registered. Use replace_existing=True to override."
            )
        
        # Validate tool class
        if not issubclass(tool_class, ToolRunner):
            raise ToolConfigError(
                tool_name,
                f"Tool class must inherit from ToolRunner, got {tool_class.__name__}"
            )
        
        self._tools[tool_name] = tool_class
        self._configs[tool_name] = config
        
        # Clear cached instance if it exists
        if tool_name in self._instances:
            del self._instances[tool_name]
    
    def get_tool(self, tool_name: str) -> ToolRunner:
        """
        Get a tool instance by name
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            ToolRunner instance
        """
        if tool_name not in self._tools:
            available_tools = list(self._tools.keys())
            raise ToolError(
                f"Tool '{tool_name}' not found. Available tools: {available_tools}",
                error_code="TOOL_NOT_FOUND"
            )
        
        # Return cached instance if available
        if tool_name in self._instances:
            return self._instances[tool_name]
        
        # Create new instance
        tool_class = self._tools[tool_name]
        config = self._configs[tool_name]
        
        try:
            instance = tool_class(config)
            self._instances[tool_name] = instance
            return instance
        except Exception as e:
            raise ToolError(
                f"Failed to instantiate tool '{tool_name}': {str(e)}",
                tool_name=tool_name,
                error_code="TOOL_INSTANTIATION_ERROR"
            )
    
    def list_tools(self) -> List[str]:
        """Get list of registered tool names"""
        return list(self._tools.keys())
    
    def get_tools_by_type(self, tool_type: ToolType) -> List[str]:
        """Get tools filtered by type"""
        return [
            name for name, config in self._configs.items()
            if config.tool_type == tool_type
        ]
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get detailed information about a tool"""
        if tool_name not in self._tools:
            raise ToolError(f"Tool '{tool_name}' not found", error_code="TOOL_NOT_FOUND")
        
        config = self._configs[tool_name]
        tool_class = self._tools[tool_name]
        
        # Get capabilities if tool is instantiated
        capabilities = {}
        if tool_name in self._instances:
            try:
                capabilities = self._instances[tool_name].get_capabilities()
            except Exception:
                capabilities = {"error": "Failed to get capabilities"}
        
        return {
            'name': tool_name,
            'class_name': tool_class.__name__,
            'module': tool_class.__module__,
            'tool_type': config.tool_type,
            'execution_mode': config.execution_mode,
            'timeout': config.timeout,
            'fallback_enabled': config.fallback_enabled,
            'capabilities': capabilities
        }
    
    def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Run health checks on all registered tools"""
        results = {}
        
        for tool_name in self._tools.keys():
            try:
                tool = self.get_tool(tool_name)
                # Note: This would need to be awaited in an async context
                results[tool_name] = {
                    'status': 'registered',
                    'instantiated': True,
                    'note': 'Health check requires async context'
                }
            except Exception as e:
                results[tool_name] = {
                    'status': 'error',
                    'instantiated': False,
                    'error': str(e)
                }
        
        return results
    
    def unregister_tool(self, tool_name: str):
        """Remove a tool from the registry"""
        if tool_name in self._tools:
            del self._tools[tool_name]
        
        if tool_name in self._configs:
            del self._configs[tool_name]
        
        if tool_name in self._instances:
            del self._instances[tool_name]
    
    def clear_cache(self, tool_name: Optional[str] = None):
        """Clear cached tool instances"""
        if tool_name:
            if tool_name in self._instances:
                del self._instances[tool_name]
        else:
            self._instances.clear()
    
    def auto_discover_tools(self, package_path: str):
        """
        Automatically discover and register tools from a package
        
        Args:
            package_path: Python package path to search for tools
        """
        try:
            package = importlib.import_module(package_path)
            
            # This is a basic implementation - in practice you'd want more
            # sophisticated discovery logic looking for ToolRunner subclasses
            for attr_name in dir(package):
                attr = getattr(package, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, ToolRunner) and 
                    attr != ToolRunner):
                    
                    # Try to create a default config
                    tool_name = attr_name.lower().replace('toolrunner', '').replace('runner', '')
                    if hasattr(attr, 'default_config'):
                        config = attr.default_config()
                    else:
                        config = ToolConfig(
                            name=tool_name,
                            tool_type=ToolType.ANALYZER  # Default type
                        )
                    
                    self.register_tool(attr, config, replace_existing=True)
                    
        except ImportError as e:
            raise ToolError(
                f"Failed to discover tools in package '{package_path}': {str(e)}",
                error_code="TOOL_DISCOVERY_ERROR"
            )


# Global registry instance
default_registry = ToolRegistry()