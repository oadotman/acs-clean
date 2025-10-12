#!/usr/bin/env python3
"""
Comprehensive Backend Audit Tool for AdCopySurge
Systematically validates all Python files, imports, and configurations
"""

import ast
import sys
import os
import importlib.util
from pathlib import Path
from typing import List, Dict, Set, Tuple, Any
import traceback
from collections import defaultdict

# Add backend to path
sys.path.insert(0, '.')

class BackendAuditor:
    def __init__(self, backend_path: str = "."):
        self.backend_path = Path(backend_path)
        self.issues = []
        self.warnings = []
        self.info = []
        
    def add_issue(self, category: str, file_path: str, message: str, line: int = None):
        """Add a critical issue that must be fixed"""
        self.issues.append({
            'category': category,
            'file': str(file_path),
            'message': message,
            'line': line,
            'severity': 'ERROR'
        })
    
    def add_warning(self, category: str, file_path: str, message: str, line: int = None):
        """Add a warning that should be reviewed"""
        self.warnings.append({
            'category': category,
            'file': str(file_path),
            'message': message,
            'line': line,
            'severity': 'WARNING'
        })
    
    def add_info(self, category: str, message: str):
        """Add informational message"""
        self.info.append({
            'category': category,
            'message': message,
            'severity': 'INFO'
        })

    def find_python_files(self) -> List[Path]:
        """Find all Python files in the backend (excluding venv/virtual environments)"""
        python_files = []
        skip_dirs = {"__pycache__", ".git", "venv", ".venv", "env", ".env", "node_modules", "build", "dist"}
        
        for path in self.backend_path.rglob("*.py"):
            # Skip virtual environments and other irrelevant directories
            path_parts = set(path.parts)
            if not any(skip_dir in path_parts for skip_dir in skip_dirs):
                python_files.append(path)
        return python_files

    def validate_syntax(self, files: List[Path]):
        """Validate Python syntax for all files"""
        print("🔍 Validating Python syntax...")
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to check syntax
                ast.parse(content, filename=str(file_path))
                
            except SyntaxError as e:
                self.add_issue(
                    "SYNTAX_ERROR",
                    file_path,
                    f"Syntax error: {e.msg}",
                    e.lineno
                )
            except UnicodeDecodeError as e:
                self.add_issue(
                    "ENCODING_ERROR", 
                    file_path,
                    f"File encoding error: {e}"
                )
            except Exception as e:
                self.add_warning(
                    "FILE_READ_ERROR",
                    file_path,
                    f"Could not read file: {e}"
                )

    def analyze_imports(self, files: List[Path]):
        """Analyze import statements and dependencies"""
        print("📦 Analyzing imports and dependencies...")
        
        all_imports = set()
        local_modules = set()
        
        # First pass: collect all local modules
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Extract module path relative to backend
                rel_path = file_path.relative_to(self.backend_path)
                if rel_path.name != "__init__.py":
                    module_path = str(rel_path.with_suffix('')).replace(os.sep, '.')
                    local_modules.add(module_path)
                
            except Exception as e:
                continue
        
        # Second pass: validate imports
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._check_import(file_path, alias.name, node.lineno)
                            all_imports.add(alias.name)
                    
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module
                        if module:
                            self._check_import(file_path, module, node.lineno)
                            all_imports.add(module)
                        
                        # Check specific imports
                        for alias in node.names:
                            import_name = f"{module}.{alias.name}" if module else alias.name
                            all_imports.add(import_name)
            
            except Exception as e:
                self.add_warning(
                    "IMPORT_ANALYSIS_ERROR",
                    file_path, 
                    f"Could not analyze imports: {e}"
                )
        
        self.add_info("IMPORTS", f"Found {len(all_imports)} unique imports across {len(files)} files")

    def _check_import(self, file_path: Path, import_name: str, line_no: int):
        """Check if an import is valid"""
        # Skip built-in modules and common third-party packages
        skip_modules = {
            'sys', 'os', 'pathlib', 'typing', 'datetime', 'uuid', 'json', 
            'ast', 'io', 'base64', 'traceback', 'collections', 'functools',
            'fastapi', 'pydantic', 'sqlalchemy', 'requests', 'httpx',
            'openai', 'transformers', 'nltk', 'numpy', 'pandas',
            'pytest', 'uvicorn', 'gunicorn', 'alembic'
        }
        
        base_module = import_name.split('.')[0]
        if base_module in skip_modules:
            return
        
        # Check local app imports
        if import_name.startswith('app.'):
            expected_path = self.backend_path / import_name.replace('.', os.sep)
            
            # Check if it's a module (directory with __init__.py)
            if (expected_path / "__init__.py").exists():
                return
            
            # Check if it's a Python file
            if expected_path.with_suffix('.py').exists():
                return
            
            self.add_issue(
                "MISSING_MODULE",
                file_path,
                f"Cannot find local module: {import_name}",
                line_no
            )

    def validate_models(self, files: List[Path]):
        """Validate SQLAlchemy model definitions"""
        print("🗃️ Validating SQLAlchemy models...")
        
        model_files = [f for f in files if 'models' in str(f) and f.name.endswith('.py')]
        
        for file_path in model_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Look for class definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        self._validate_model_class(file_path, node, content)
            
            except Exception as e:
                self.add_warning(
                    "MODEL_VALIDATION_ERROR",
                    file_path,
                    f"Could not validate model: {e}"
                )

    def _validate_model_class(self, file_path: Path, class_node: ast.ClassDef, content: str):
        """Validate a specific model class"""
        class_name = class_node.name
        
        # Check if it inherits from Base
        inherits_from_base = any(
            (isinstance(base, ast.Name) and base.id == 'Base') or
            (isinstance(base, ast.Attribute) and base.attr == 'Base')
            for base in class_node.bases
        )
        
        if inherits_from_base:
            # This is likely a SQLAlchemy model
            has_tablename = False
            has_columns = False
            
            for node in ast.walk(class_node):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id == '__tablename__':
                                has_tablename = True
                            elif 'Column(' in content:  # Simple check for Column usage
                                has_columns = True
            
            if not has_tablename:
                self.add_warning(
                    "MODEL_MISSING_TABLENAME",
                    file_path,
                    f"Model {class_name} missing __tablename__"
                )
            
            if not has_columns:
                self.add_warning(
                    "MODEL_NO_COLUMNS",
                    file_path,
                    f"Model {class_name} appears to have no Column definitions"
                )

    def validate_services(self, files: List[Path]):
        """Validate service classes"""
        print("⚙️ Validating service classes...")
        
        service_files = [f for f in files if 'services' in str(f) and f.name.endswith('.py')]
        
        for file_path in service_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                # Look for service classes
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name.endswith('Service'):
                        self._validate_service_class(file_path, node, content)
            
            except Exception as e:
                self.add_warning(
                    "SERVICE_VALIDATION_ERROR",
                    file_path,
                    f"Could not validate service: {e}"
                )

    def _validate_service_class(self, file_path: Path, class_node: ast.ClassDef, content: str):
        """Validate a service class"""
        class_name = class_node.name
        
        # Check if it has __init__ method
        has_init = any(
            isinstance(node, ast.FunctionDef) and node.name == '__init__'
            for node in class_node.body
        )
        
        if not has_init:
            self.add_warning(
                "SERVICE_NO_INIT",
                file_path,
                f"Service {class_name} has no __init__ method"
            )

    def validate_api_routes(self, files: List[Path]):
        """Validate FastAPI route definitions"""
        print("🛣️ Validating API routes...")
        
        api_files = [f for f in files if 'api' in str(f) and f.name.endswith('.py')]
        
        for file_path in api_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for common patterns
                if 'APIRouter()' in content or 'router = APIRouter()' in content:
                    if '@router.' not in content:
                        self.add_warning(
                            "API_NO_ROUTES",
                            file_path,
                            "API file has router but no route definitions"
                        )
            
            except Exception as e:
                self.add_warning(
                    "API_VALIDATION_ERROR",
                    file_path,
                    f"Could not validate API routes: {e}"
                )

    def run_comprehensive_audit(self):
        """Run the complete audit"""
        print("🚀 Starting Comprehensive Backend Audit")
        print("=" * 60)
        
        # Find all Python files
        python_files = self.find_python_files()
        self.add_info("FILES", f"Found {len(python_files)} Python files to audit")
        
        # Run all validations
        self.validate_syntax(python_files)
        self.analyze_imports(python_files)
        self.validate_models(python_files) 
        self.validate_services(python_files)
        self.validate_api_routes(python_files)
        
        # Report results
        self.print_report()
        
        return len(self.issues) == 0

    def print_report(self):
        """Print the audit report"""
        print("\n📊 AUDIT REPORT")
        print("=" * 60)
        
        # Summary
        print(f"🔍 Files Audited: {len(self.find_python_files())}")
        print(f"❌ Critical Issues: {len(self.issues)}")
        print(f"⚠️ Warnings: {len(self.warnings)}")
        print(f"ℹ️ Info Messages: {len(self.info)}")
        
        # Critical Issues
        if self.issues:
            print(f"\n❌ CRITICAL ISSUES ({len(self.issues)}):")
            print("-" * 40)
            for issue in self.issues:
                line_info = f" (line {issue['line']})" if issue['line'] else ""
                print(f"📁 {issue['file']}{line_info}")
                print(f"   {issue['category']}: {issue['message']}")
                print()
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            print("-" * 40)
            for warning in self.warnings[:10]:  # Show first 10 warnings
                line_info = f" (line {warning['line']})" if warning['line'] else ""
                print(f"📁 {warning['file']}{line_info}")
                print(f"   {warning['category']}: {warning['message']}")
            
            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more warnings")
            print()
        
        # Info
        if self.info:
            print(f"\nℹ️ INFORMATION:")
            print("-" * 20)
            for info in self.info:
                print(f"   {info['category']}: {info['message']}")
        
        # Final verdict
        print(f"\n{'🎉 AUDIT PASSED' if len(self.issues) == 0 else '💥 AUDIT FAILED'}")
        print("=" * 60)


if __name__ == "__main__":
    auditor = BackendAuditor()
    success = auditor.run_comprehensive_audit()
    sys.exit(0 if success else 1)
