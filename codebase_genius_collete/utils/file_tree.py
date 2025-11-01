"""
File Tree Generation Utilities.

Provides constants for ignoring common directories/files and
a helper function to generate a markdown file tree from the graph.
"""
import os

# --- Constants (Imported by Jac) ---

# Directories to ignore during repository mapping
IGNORE_DIRS = {
    '.git', 
    'node_modules', 
    '__pycache__', 
    'venv', 
    '.venv', 
    'env',
    'ENV',
    'dist', 
    'build',
    '.vscode',
    '.idea',
    '.mypy_cache',
    '.jac_cache'
}

# Files to ignore during repository mapping
IGNORE_FILES = {
    '.DS_Store', 
    '.env', 
    '*.pyc', 
    '*.pyo',
    '*.swp',
    '*.swo'
}


# --- Helper Function (Imported by Jac) ---

def generate_file_tree_md(repo_node) -> str:
    """
    Generates a pretty textual tree of files from the graph nodes.
    
    This function is called by doc_genie and traverses the graph
    nodes, not the file system.
    
    Args:
        repo_node: The root node::repository of the graph.
        
    Returns:
        A string formatted as a markdown code block for the file tree.
    """
    tree_lines = [f"{repo_node.name}/"]
    
    # Use a recursive helper function to walk the graph
    _build_tree_recursive(repo_node, tree_lines, prefix="    ")
    
    return "\n".join(tree_lines)

def _build_tree_recursive(parent_node, tree_lines: list, prefix: str):
    """
    Recursively build the file tree by walking graph nodes.
    
    Args:
        parent_node: The current node (repository or folder).
        tree_lines: The list of strings to append to.
        prefix: The indentation prefix for the current level.
    """
    
    # Get all folder and file children of the current node
    # We rely on the graph connection (e.g., node::repository +> node::folder)
    folders = [edge.target for edge in parent_node.edges_out if edge.target.kind == 'folder']
    files = [edge.target for edge in parent_node.edges_out if edge.target.kind == 'file']
    
    # Sort folders and files by name
    folders.sort(key=lambda x: x.name)
    files.sort(key=lambda x: x.name)
    
    # Process all folders first
    for i, folder in enumerate(folders):
        is_last_item = (i == len(folders) - 1) and (len(files) == 0)
        
        if is_last_item:
            tree_lines.append(f"{prefix}└── {folder.name}/")
            new_prefix = f"{prefix}    "
        else:
            tree_lines.append(f"{prefix}├── {folder.name}/")
            new_prefix = f"{prefix}│   "
            
        # Recurse into the subfolder
        _build_tree_recursive(folder, tree_lines, new_prefix)
        
    # Process all files
    for i, file in enumerate(files):
        is_last_file = (i == len(files) - 1)
        
        if is_last_file:
            tree_lines.append(f"{prefix}└── {file.name}")
        else:
            tree_lines.append(f"{prefix}├── {file.name}")
