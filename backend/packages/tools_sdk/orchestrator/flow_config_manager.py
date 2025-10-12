"""
Flow Configuration Manager - Manages and persists tool flow configurations
Handles loading, saving, validation, and versioning of flow configurations
"""

import json
import yaml
import os
import time
from typing import Dict, Any, List, Optional, Union, Set
from dataclasses import asdict, dataclass
from pathlib import Path
import logging

from .tools_flow_orchestrator import (
    FlowConfiguration, ToolFlowStep, FlowExecutionStrategy, FlowPriority
)
from ..core import ToolConfig, ToolType


@dataclass
class FlowTemplate:
    """Template definition for reusable flow configurations"""
    template_id: str
    name: str
    description: str
    category: str
    tags: List[str]
    configuration: FlowConfiguration
    created_at: float
    updated_at: float
    version: str = "1.0.0"
    author: str = "system"
    usage_count: int = 0


@dataclass
class FlowConfigurationHistory:
    """Track configuration change history"""
    timestamp: float
    version: str
    changes: Dict[str, Any]
    author: str
    description: str


class FlowConfigurationManager:
    """
    Manages flow configurations with persistence, versioning, and templates
    
    Features:
    - Save/load flow configurations to/from JSON/YAML
    - Template management for common flow patterns
    - Configuration validation and schema checking
    - Version control and change tracking
    - Configuration sharing and export/import
    - Dynamic configuration updates
    """
    
    def __init__(self, config_directory: str = None):
        self.logger = logging.getLogger(__name__)
        
        # Set up configuration directory
        if config_directory:
            self.config_dir = Path(config_directory)
        else:
            # Default to SDK directory
            sdk_dir = Path(__file__).parent.parent
            self.config_dir = sdk_dir / "configurations" / "flows"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories for organization
        self.templates_dir = self.config_dir / "templates"
        self.custom_dir = self.config_dir / "custom"
        self.history_dir = self.config_dir / "history"
        
        for directory in [self.templates_dir, self.custom_dir, self.history_dir]:
            directory.mkdir(exist_ok=True)
        
        # In-memory cache
        self.loaded_configurations: Dict[str, FlowConfiguration] = {}
        self.templates_cache: Dict[str, FlowTemplate] = {}
        self.configuration_history: Dict[str, List[FlowConfigurationHistory]] = {}
        
        # Load existing configurations
        self._load_all_configurations()
        
        # Tool registry for validation
        self.available_tools = {
            'performance_forensics': 'PerformanceForensicsToolRunner',
            'psychology_scorer': 'PsychologyScorerToolRunner', 
            'brand_voice_engine': 'BrandVoiceEngineToolRunner',
            'legal_risk_scanner': 'LegalRiskScannerToolRunner'
        }
    
    def save_configuration(self, flow_config: FlowConfiguration, 
                          category: str = "custom", 
                          format: str = "json",
                          author: str = "user") -> bool:
        """Save a flow configuration to disk"""
        try:
            # Determine file path
            if category == "template":
                file_path = self.templates_dir / f"{flow_config.flow_id}.{format}"
            else:
                file_path = self.custom_dir / f"{flow_config.flow_id}.{format}"
            
            # Convert to serializable format
            config_data = self._flow_config_to_dict(flow_config)
            
            # Add metadata
            config_data['metadata'] = {
                'saved_at': time.time(),
                'author': author,
                'category': category,
                'version': "1.0.0"
            }
            
            # Save in specified format
            if format.lower() == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
            elif format.lower() in ["yaml", "yml"]:
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Update cache
            self.loaded_configurations[flow_config.flow_id] = flow_config
            
            # Record change history
            self._record_configuration_change(
                flow_config.flow_id, "created", author, "Configuration saved"
            )
            
            self.logger.info(f"Flow configuration saved: {flow_config.flow_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration {flow_config.flow_id}: {str(e)}")
            return False
    
    def load_configuration(self, flow_id: str, reload: bool = False) -> Optional[FlowConfiguration]:
        """Load a flow configuration by ID"""
        
        # Return cached version if available and not forcing reload
        if not reload and flow_id in self.loaded_configurations:
            return self.loaded_configurations[flow_id]
        
        # Search for configuration file
        config_file = self._find_configuration_file(flow_id)
        if not config_file:
            self.logger.warning(f"Configuration not found: {flow_id}")
            return None
        
        try:
            # Load configuration data
            config_data = self._load_config_file(config_file)
            
            # Convert to FlowConfiguration object
            flow_config = self._dict_to_flow_config(config_data)
            
            # Cache the loaded configuration
            self.loaded_configurations[flow_id] = flow_config
            
            self.logger.info(f"Flow configuration loaded: {flow_id}")
            return flow_config
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration {flow_id}: {str(e)}")
            return None
    
    def create_template(self, flow_config: FlowConfiguration,
                       name: str,
                       description: str,
                       category: str = "general",
                       tags: List[str] = None,
                       author: str = "user") -> FlowTemplate:
        """Create a reusable template from a flow configuration"""
        
        template = FlowTemplate(
            template_id=flow_config.flow_id,
            name=name,
            description=description,
            category=category,
            tags=tags or [],
            configuration=flow_config,
            created_at=time.time(),
            updated_at=time.time(),
            author=author
        )
        
        # Save template
        self._save_template(template)
        
        # Cache template
        self.templates_cache[template.template_id] = template
        
        return template
    
    def get_template(self, template_id: str) -> Optional[FlowTemplate]:
        """Get a template by ID"""
        if template_id in self.templates_cache:
            return self.templates_cache[template_id]
        
        # Try to load from disk
        template_file = self.templates_dir / f"{template_id}.json"
        if template_file.exists():
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                template = self._dict_to_template(template_data)
                self.templates_cache[template_id] = template
                return template
                
            except Exception as e:
                self.logger.error(f"Failed to load template {template_id}: {str(e)}")
        
        return None
    
    def list_configurations(self, category: str = "all") -> Dict[str, Dict[str, Any]]:
        """List all available configurations"""
        configurations = {}
        
        # Scan directories based on category
        if category in ["all", "custom"]:
            for config_file in self.custom_dir.glob("*.json"):
                config_info = self._get_config_info(config_file)
                if config_info:
                    configurations[config_info['flow_id']] = {
                        **config_info,
                        'category': 'custom'
                    }
        
        if category in ["all", "template"]:
            for template_file in self.templates_dir.glob("*.json"):
                config_info = self._get_config_info(template_file)
                if config_info:
                    configurations[config_info['flow_id']] = {
                        **config_info,
                        'category': 'template'
                    }
        
        return configurations
    
    def list_templates(self, category: str = None) -> Dict[str, FlowTemplate]:
        """List available templates, optionally filtered by category"""
        if category:
            return {
                template_id: template 
                for template_id, template in self.templates_cache.items()
                if template.category == category
            }
        else:
            return self.templates_cache.copy()
    
    def validate_configuration(self, flow_config: FlowConfiguration) -> Dict[str, Any]:
        """Validate a flow configuration"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check basic structure
        if not flow_config.flow_id:
            validation_result['errors'].append("Flow ID is required")
            validation_result['valid'] = False
        
        if not flow_config.steps:
            validation_result['errors'].append("At least one step is required")
            validation_result['valid'] = False
        
        # Validate steps
        for i, step in enumerate(flow_config.steps):
            step_errors = self._validate_step(step, i)
            validation_result['errors'].extend(step_errors)
            if step_errors:
                validation_result['valid'] = False
        
        # Check for circular dependencies
        if self._has_circular_dependencies(flow_config.steps):
            validation_result['errors'].append("Circular dependencies detected")
            validation_result['valid'] = False
        
        # Performance suggestions
        if len(flow_config.steps) > 2 and flow_config.execution_strategy == FlowExecutionStrategy.SEQUENTIAL:
            validation_result['suggestions'].append(
                "Consider using parallel execution for better performance"
            )
        
        # Timeout warnings
        if flow_config.total_timeout and flow_config.total_timeout < 30:
            validation_result['warnings'].append(
                "Total timeout may be too low for complex analysis"
            )
        
        return validation_result
    
    def duplicate_configuration(self, flow_id: str, new_flow_id: str) -> Optional[FlowConfiguration]:
        """Create a copy of an existing configuration"""
        original = self.load_configuration(flow_id)
        if not original:
            return None
        
        # Create duplicate with new ID
        duplicate_data = self._flow_config_to_dict(original)
        duplicate_data['flow_id'] = new_flow_id
        duplicate_data['name'] = f"{original.name} (Copy)"
        
        duplicate_config = self._dict_to_flow_config(duplicate_data)
        
        # Save duplicate
        if self.save_configuration(duplicate_config, author="system"):
            return duplicate_config
        
        return None
    
    def delete_configuration(self, flow_id: str, category: str = "custom") -> bool:
        """Delete a configuration"""
        try:
            # Find and delete file
            if category == "template":
                file_path = self.templates_dir / f"{flow_id}.json"
            else:
                file_path = self.custom_dir / f"{flow_id}.json"
            
            if file_path.exists():
                file_path.unlink()
            
            # Remove from cache
            if flow_id in self.loaded_configurations:
                del self.loaded_configurations[flow_id]
            
            if flow_id in self.templates_cache:
                del self.templates_cache[flow_id]
            
            # Record deletion
            self._record_configuration_change(
                flow_id, "deleted", "user", "Configuration deleted"
            )
            
            self.logger.info(f"Configuration deleted: {flow_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete configuration {flow_id}: {str(e)}")
            return False
    
    def export_configuration(self, flow_id: str, export_path: str, 
                           include_history: bool = False) -> bool:
        """Export a configuration to external file"""
        try:
            config = self.load_configuration(flow_id)
            if not config:
                return False
            
            export_data = {
                'configuration': self._flow_config_to_dict(config),
                'exported_at': time.time(),
                'version': "1.0.0"
            }
            
            if include_history and flow_id in self.configuration_history:
                export_data['history'] = [
                    asdict(history_entry) 
                    for history_entry in self.configuration_history[flow_id]
                ]
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration exported: {flow_id} -> {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export configuration {flow_id}: {str(e)}")
            return False
    
    def import_configuration(self, import_path: str, 
                           category: str = "custom") -> Optional[FlowConfiguration]:
        """Import a configuration from external file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Extract configuration
            if 'configuration' in import_data:
                config_data = import_data['configuration']
            else:
                config_data = import_data  # Assume direct configuration format
            
            # Convert to FlowConfiguration
            flow_config = self._dict_to_flow_config(config_data)
            
            # Validate before saving
            validation = self.validate_configuration(flow_config)
            if not validation['valid']:
                self.logger.error(f"Invalid configuration in import: {validation['errors']}")
                return None
            
            # Save imported configuration
            if self.save_configuration(flow_config, category=category, author="imported"):
                # Import history if available
                if 'history' in import_data:
                    history_entries = [
                        FlowConfigurationHistory(**entry) 
                        for entry in import_data['history']
                    ]
                    self.configuration_history[flow_config.flow_id] = history_entries
                
                self.logger.info(f"Configuration imported: {flow_config.flow_id}")
                return flow_config
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to import configuration from {import_path}: {str(e)}")
            return None
    
    def get_configuration_history(self, flow_id: str) -> List[FlowConfigurationHistory]:
        """Get change history for a configuration"""
        return self.configuration_history.get(flow_id, [])
    
    def _load_all_configurations(self):
        """Load all configurations into cache on startup"""
        # Load custom configurations
        for config_file in self.custom_dir.glob("*.json"):
            try:
                config_data = self._load_config_file(config_file)
                flow_config = self._dict_to_flow_config(config_data)
                self.loaded_configurations[flow_config.flow_id] = flow_config
            except Exception as e:
                self.logger.warning(f"Failed to load configuration {config_file}: {str(e)}")
        
        # Load templates
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                template = self._dict_to_template(template_data)
                self.templates_cache[template.template_id] = template
            except Exception as e:
                self.logger.warning(f"Failed to load template {template_file}: {str(e)}")
    
    def _find_configuration_file(self, flow_id: str) -> Optional[Path]:
        """Find configuration file by flow ID"""
        # Check custom configurations first
        for ext in ["json", "yaml", "yml"]:
            custom_path = self.custom_dir / f"{flow_id}.{ext}"
            if custom_path.exists():
                return custom_path
        
        # Check templates
        for ext in ["json", "yaml", "yml"]:
            template_path = self.templates_dir / f"{flow_id}.{ext}"
            if template_path.exists():
                return template_path
        
        return None
    
    def _load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration data from file"""
        if file_path.suffix.lower() == ".json":
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        elif file_path.suffix.lower() in [".yaml", ".yml"]:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _flow_config_to_dict(self, flow_config: FlowConfiguration) -> Dict[str, Any]:
        """Convert FlowConfiguration to dictionary"""
        return {
            'flow_id': flow_config.flow_id,
            'name': flow_config.name,
            'description': flow_config.description,
            'execution_strategy': flow_config.execution_strategy.value,
            'priority': flow_config.priority.value,
            'max_parallel_workers': flow_config.max_parallel_workers,
            'total_timeout': flow_config.total_timeout,
            'continue_on_error': flow_config.continue_on_error,
            'output_aggregation_strategy': flow_config.output_aggregation_strategy,
            'steps': [
                {
                    'tool_name': step.tool_name,
                    'tool_class': step.tool_class.__name__,
                    'config': asdict(step.config),
                    'dependencies': list(step.dependencies),
                    'parallel_group': step.parallel_group,
                    'required': step.required,
                    'timeout_override': step.timeout_override,
                    'retry_count': step.retry_count
                }
                for step in flow_config.steps
            ]
        }
    
    def _dict_to_flow_config(self, config_data: Dict[str, Any]) -> FlowConfiguration:
        """Convert dictionary to FlowConfiguration"""
        from ..tools.performance_forensics_tool import PerformanceForensicsToolRunner
        from ..tools.psychology_scorer_tool import PsychologyScorerToolRunner
        from ..tools.brand_voice_engine_tool import BrandVoiceEngineToolRunner
        from ..tools.legal_risk_scanner_tool import LegalRiskScannerToolRunner
        
        # Tool class mapping
        tool_classes = {
            'PerformanceForensicsToolRunner': PerformanceForensicsToolRunner,
            'PsychologyScorerToolRunner': PsychologyScorerToolRunner,
            'BrandVoiceEngineToolRunner': BrandVoiceEngineToolRunner,
            'LegalRiskScannerToolRunner': LegalRiskScannerToolRunner
        }
        
        # Convert steps
        steps = []
        for step_data in config_data.get('steps', []):
            tool_class = tool_classes.get(step_data['tool_class'])
            if not tool_class:
                raise ValueError(f"Unknown tool class: {step_data['tool_class']}")
            
            # Reconstruct ToolConfig
            config_dict = step_data['config']
            tool_config = ToolConfig(
                name=config_dict['name'],
                tool_type=ToolType(config_dict['tool_type']),
                timeout=config_dict['timeout'],
                parameters=config_dict['parameters']
            )
            
            step = ToolFlowStep(
                tool_name=step_data['tool_name'],
                tool_class=tool_class,
                config=tool_config,
                dependencies=set(step_data.get('dependencies', [])),
                parallel_group=step_data.get('parallel_group'),
                required=step_data.get('required', True),
                timeout_override=step_data.get('timeout_override'),
                retry_count=step_data.get('retry_count', 1)
            )
            steps.append(step)
        
        return FlowConfiguration(
            flow_id=config_data['flow_id'],
            name=config_data['name'],
            description=config_data['description'],
            steps=steps,
            execution_strategy=FlowExecutionStrategy(config_data.get('execution_strategy', 'mixed')),
            priority=FlowPriority(config_data.get('priority', 2)),
            max_parallel_workers=config_data.get('max_parallel_workers', 4),
            total_timeout=config_data.get('total_timeout'),
            continue_on_error=config_data.get('continue_on_error', True),
            output_aggregation_strategy=config_data.get('output_aggregation_strategy', 'weighted_average')
        )
    
    def _save_template(self, template: FlowTemplate):
        """Save template to disk"""
        template_file = self.templates_dir / f"{template.template_id}.json"
        template_data = asdict(template)
        
        # Convert FlowConfiguration to dict
        template_data['configuration'] = self._flow_config_to_dict(template.configuration)
        
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
    
    def _dict_to_template(self, template_data: Dict[str, Any]) -> FlowTemplate:
        """Convert dictionary to FlowTemplate"""
        flow_config = self._dict_to_flow_config(template_data['configuration'])
        
        return FlowTemplate(
            template_id=template_data['template_id'],
            name=template_data['name'],
            description=template_data['description'],
            category=template_data['category'],
            tags=template_data['tags'],
            configuration=flow_config,
            created_at=template_data['created_at'],
            updated_at=template_data['updated_at'],
            version=template_data.get('version', '1.0.0'),
            author=template_data.get('author', 'system'),
            usage_count=template_data.get('usage_count', 0)
        )
    
    def _get_config_info(self, config_file: Path) -> Optional[Dict[str, Any]]:
        """Get basic info about a configuration file"""
        try:
            config_data = self._load_config_file(config_file)
            return {
                'flow_id': config_data.get('flow_id'),
                'name': config_data.get('name'),
                'description': config_data.get('description'),
                'execution_strategy': config_data.get('execution_strategy'),
                'step_count': len(config_data.get('steps', [])),
                'file_path': str(config_file)
            }
        except Exception as e:
            self.logger.warning(f"Failed to read config info from {config_file}: {str(e)}")
            return None
    
    def _validate_step(self, step: ToolFlowStep, step_index: int) -> List[str]:
        """Validate a single step"""
        errors = []
        
        if not step.tool_name:
            errors.append(f"Step {step_index}: Tool name is required")
        
        if step.tool_name not in self.available_tools:
            errors.append(f"Step {step_index}: Unknown tool '{step.tool_name}'")
        
        if not step.config:
            errors.append(f"Step {step_index}: Tool configuration is required")
        
        if step.timeout_override and step.timeout_override <= 0:
            errors.append(f"Step {step_index}: Invalid timeout override")
        
        return errors
    
    def _has_circular_dependencies(self, steps: List[ToolFlowStep]) -> bool:
        """Check for circular dependencies in steps"""
        dependencies = {step.tool_name: step.dependencies for step in steps}
        
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in dependencies.get(node, set()):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for tool_name in dependencies:
            if has_cycle(tool_name):
                return True
        
        return False
    
    def _record_configuration_change(self, flow_id: str, change_type: str, 
                                   author: str, description: str):
        """Record a configuration change in history"""
        if flow_id not in self.configuration_history:
            self.configuration_history[flow_id] = []
        
        change_record = FlowConfigurationHistory(
            timestamp=time.time(),
            version="1.0.0",  # Would be incremented in a real system
            changes={
                'type': change_type,
                'description': description
            },
            author=author,
            description=description
        )
        
        self.configuration_history[flow_id].append(change_record)
        
        # Keep only last 50 history entries per configuration
        if len(self.configuration_history[flow_id]) > 50:
            self.configuration_history[flow_id] = self.configuration_history[flow_id][-50:]