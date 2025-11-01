"""
Python and Jac Parser Utility - AST-based Code Analysis

This module uses Python's Abstract Syntax Tree (AST) module to parse
Python source files and regex-based parsing for Jac files to extract:
- Functions (with parameters, return types, docstrings)
- Classes (with methods, attributes, inheritance)
- Walkers, Nodes, Edges (Jac constructs)
- Imports (modules and their aliases)
- Relationships (function calls, inheritance)

The extracted data is used to build the Code Context Graph (CCG).
"""

import ast
import re
from typing import Dict, Any, List

# --- Python AST Parsing (CodeVisitor) ---

class CodeVisitor(ast.NodeVisitor):
    """
    AST Visitor that walks through Python code and extracts structure.
    
    This class extends ast.NodeVisitor to traverse the Abstract Syntax Tree
    and collect information about functions, classes, and their relationships.
    """
    
    def __init__(self, file_path: str):
        """Initialize empty data structures for collected information."""
        self.file_path = file_path
        self.functions: List[Dict[str, Any]] = []
        self.classes: List[Dict[str, Any]] = []
        self.imports: List[Dict[str, Any]] = []
        self.relationships: List[Dict[str, Any]] = []
        self.current_func: Optional[Dict[str, Any]] = None
        self.current_class: Optional[Dict[str, Any]] = None

    def visit_Import(self, node: ast.Import):
        """Visit an import statement (e.g., import os, import sys)"""
        for alias in node.names:
            self.imports.append({
                'module': alias.name,
                'alias': alias.asname,
                'line': node.lineno
            })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Visit a from-import statement (e.g., from os import path)"""
        module_name = node.module or "UNKNOWN"
        for alias in node.names:
            full_module = f"{module_name}.{alias.name}"
            self.imports.append({
                'module': full_module,
                'alias': alias.asname,
                'line': node.lineno
            })
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit a function definition"""
        func_info: Dict[str, Any] = {
            'name': node.name,
            'params': [arg.arg for arg in node.args.args],
            'returns': self._get_return_type(node),
            'docstring': ast.get_docstring(node),
            'line': node.lineno,
            'file_path': self.file_path,
            'calls': [],
            'decorators': [self._get_decorator_name(dec) for dec in node.decorator_list]
        }
        
        if self.current_class:
            func_info['parent_class'] = self.current_class['name']
        
        # Set current function context
        parent_func = self.current_func
        self.current_func = func_info
        
        self.functions.append(func_info)
        self.generic_visit(node) # Visit children (like calls inside)
        
        # Restore parent function context
        self.current_func = parent_func

    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit a class definition"""
        class_info: Dict[str, Any] = {
            'name': node.name,
            'bases': [self._get_base_name(b) for b in node.bases if self._get_base_name(b)],
            'methods': [],
            'attributes': [],
            'docstring': ast.get_docstring(node),
            'line': node.lineno,
            'file_path': self.file_path
        }
        
        # Add inheritance relationships
        for base in class_info['bases']:
            self.relationships.append({
                'from': node.name,
                'to': base,
                'type': 'inherits',
                'line': node.lineno
            })
        
        self.classes.append(class_info)
        
        # Set current class context
        parent_class = self.current_class
        self.current_class = class_info
        
        # Manually visit body to find methods and attributes
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info['methods'].append(item.name)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_info['attributes'].append(target.id)
            elif isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    class_info['attributes'].append(item.target.id)

        self.generic_visit(node) # Visit children (like methods)
        
        # Restore parent class context
        self.current_class = parent_class

    def visit_Call(self, node: ast.Call):
        """Visit a function call"""
        func_name = self._get_call_name(node.func)
        
        if func_name and self.current_func:
            # Add to the function's list of calls
            self.current_func['calls'].append(func_name)
            
            # Add to the global relationships list
            self.relationships.append({
                'from': self.current_func['name'],
                'to': func_name,
                'type': 'calls',
                'line': node.lineno
            })
        
        self.generic_visit(node)

    # --- Helper Methods for AST Visitor ---

    def _get_call_name(self, node: ast.AST) -> Optional[str]:
        """Extract function name from a Call node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # This gets the method name (e.g., 'append' from 'my_list.append')
            return node.attr
        return None

    def _get_base_name(self, node: ast.AST) -> Optional[str]:
        """Extract base class name"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # e.g., inherits from some_module.BaseClass
            return f"{self._get_base_name(node.value)}.{node.attr}"
        return None

    def _get_decorator_name(self, node: ast.AST) -> Optional[str]:
        """Extract decorator name"""
        return self._get_base_name(node) # Uses the same logic as base names

    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation if present"""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Constant):
                return str(node.returns.value)
            elif isinstance(node.returns, ast.Attribute):
                return self._get_base_name(node.returns)
            elif isinstance(node.returns, ast.Subscript):
                # Handles types like list[str] or dict[str, int]
                # We'll just get the base type (e.g., 'list' or 'dict')
                if hasattr(node.returns.value, 'id'):
                     return node.returns.value.id
        return None


# --- Jac Regex-Based Parsing ---

# Regex patterns for Jac constructs
# We use re.DOTALL so '.' matches newlines, and re.MULTILINE for '^'
JAC_WALKER_PATTERN = re.compile(r'^\s*walker\s+([\w_]+)\s*\{([^}]+)\}', re.MULTILINE | re.DOTALL)
JAC_NODE_PATTERN = re.compile(r'^\s*node\s+([\w_]+)\s*\{([^}]+)\}', re.MULTILINE | re.DOTALL)
JAC_EDGE_PATTERN = re.compile(r'^\s*edge\s+([\w_]+)\s*\{([^}]+)\}', re.MULTILINE | re.DOTALL)
JAC_ABILITY_PATTERN = re.compile(r'^\s*(can\s+[\w_]+|test\s+[\w_]+)\s*(\(.*\))?\s*(->\s*[\w_:\.\[\]]+)?\s*\{', re.MULTILINE)
JAC_HAS_PATTERN = re.compile(r'^\s*has\s+([\w_]+)\s*:\s*([^;=]+)', re.MULTILINE)
JAC_IMPORT_PATTERN = re.compile(r'^\s*import:jac\s+from\s+([\w\._]+)\s*\{([^}]+)\}', re.MULTILINE | re.DOTALL)


# --- Jac-Exportable Functions ---

def parse_python_file(path: str) -> Dict[str, Any]:
    """
    Parse a Python file and return extracted code structure.
    
    Args:
        path: Path to the Python file
        
    Returns:
        Dictionary containing extracted data and relationships.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            tree = ast.parse(content, filename=path)
        
        visitor = CodeVisitor(file_path=path)
        visitor.visit(tree)
        
        return {
            'functions': visitor.functions,
            'classes': visitor.classes,
            'imports': visitor.imports,
            'relationships': visitor.relationships,
            'walkers': [], 'nodes': [], 'edges': [], 'abilities': [], 'error': None
        }
    except Exception as e:
        return {'error': str(e)}


def parse_jac_file(path: str) -> Dict[str, Any]:
    """
    Basic parser for Jac files using regex.
    
    Args:
        path: Path to the Jac file
        
    Returns:
        Dictionary containing extracted data.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        walkers, abilities, walker_has_vars = _parse_jac_walkers(content, path)
        nodes, node_has_vars = _parse_jac_nodes_edges(content, path, JAC_NODE_PATTERN, 'node')
        edges, edge_has_vars = _parse_jac_nodes_edges(content, path, JAC_EDGE_PATTERN, 'edge')
        imports = _parse_jac_imports(content, path)
        
        # Combine all extracted abilities
        all_abilities = abilities + _parse_jac_abilities(content, path)
        
        return {
            'walkers': walkers,
            'nodes': nodes,
            'edges': edges,
            'abilities': all_abilities,
            'imports': imports,
            'functions': [], 'classes': [], 'relationships': [], 'error': None
        }
    
    except Exception as e:
        return {'error': str(e)}

def parse_file_by_extension(path: str) -> Dict[str, Any]:
    """
    Parse a file based on its extension (.py or .jac).
    
    Args:
        path: Path to the file
        
    Returns:
        Parsed data dictionary
    """
    if path.endswith('.py'):
        return parse_python_file(path)
    elif path.endswith('.jac'):
        return parse_jac_file(path)
    else:
        return {'error': f'Unsupported file type: {path}'}

# --- Internal Helper Functions for Jac Parsing ---

def _parse_jac_walkers(content: str, path: str) -> tuple:
    """Extract walkers, their abilities, and their 'has' variables."""
    walkers = []
    abilities = []
    has_vars = []
    
    for match in JAC_WALKER_PATTERN.finditer(content):
        name = match.group(1)
        body = match.group(2)
        line = content[:match.start()].count('\n') + 1
        
        # Find abilities within this walker
        for ab_match in JAC_ABILITY_PATTERN.finditer(body):
            sig = ab_match.group(0).replace('{', '').strip()
            ab_name = sig.split('(')[0].replace('can ', '').replace('test ', '').strip()
            ab_line = line + body[:ab_match.start()].count('\n') + 1
            abilities.append({
                'name': ab_name,
                'signature': sig,
                'ability_type': 'can' if 'can' in sig else 'test',
                'parent_walker': name,
                'docstring': None, # Note: regex doesn't easily get docstrings
                'line': ab_line,
                'file_path': path
            })
            
        # Find 'has' variables
        walker_has = []
        for has_match in JAC_HAS_PATTERN.finditer(body):
            has_sig = has_match.group(0).replace('has ', '').strip()
            walker_has.append(has_sig)
            
        walkers.append({
            'name': name,
            'docstring': None,
            'attributes': walker_has,
            'line': line,
            'file_path': path
        })
        has_vars.extend(walker_has)
        
    return walkers, abilities, has_vars

def _parse_jac_nodes_edges(content: str, path: str, pattern: re.Pattern, kind: str) -> tuple:
    """Extract nodes or edges and their 'has' variables."""
    elements = []
    has_vars = []
    
    for match in pattern.finditer(content):
        name = match.group(1)
        body = match.group(2)
        line = content[:match.start()].count('\n') + 1
        
        element_has = []
        for has_match in JAC_HAS_PATTERN.finditer(body):
            has_sig = has_match.group(0).replace('has ', '').strip()
            element_has.append(has_sig)
            
        elements.append({
            'name': name,
            'kind': kind,
            'attributes': element_has,
            'line': line,
            'file_path': path
        })
        has_vars.extend(element_has)
        
    return elements, has_vars

def _parse_jac_abilities(content: str, path: str) -> list:
    """Extract standalone abilities (not inside a walker)."""
    # This is a simplification; we're just finding *all* abilities
    # and the walker parser finds the ones *inside* walkers.
    # A more robust parser would differentiate.
    abilities = []
    for ab_match in JAC_ABILITY_PATTERN.finditer(content):
        sig = ab_match.group(0).replace('{', '').strip()
        ab_name = sig.split('(')[0].replace('can ', '').replace('test ', '').strip()
        ab_line = content[:ab_match.start()].count('\n') + 1
        abilities.append({
            'name': ab_name,
            'signature': sig,
            'ability_type': 'can' if 'can' in sig else 'test',
            'parent_walker': None, # Standalone
            'docstring': None,
            'line': ab_line,
            'file_path': path
        })
    return abilities

def _parse_jac_imports(content: str, path: str) -> list:
    """Extract Jac imports."""
    imports = []
    for match in JAC_IMPORT_PATTERN.finditer(content):
        module = match.group(1)
        items = [item.strip() for item in match.group(2).split(',')]
        line = content[:match.start()].count('\n') + 1
        
        for item in items:
            imports.append({
                'module': f"{module}.{item}",
                'alias': None,
                'line': line
            })
    return imports

