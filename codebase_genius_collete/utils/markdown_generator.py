"""
Markdown Generation Utilities.

Provides helper functions to convert the Code Context Graph (CCG) data
into well-formatted Markdown, including Mermaid diagrams.
"""

# --- Constants ---
MAX_MERMAID_NODES = 25  # Max nodes for function call graph
MAX_CLASS_ATTRIBUTES = 7 # Max attributes to show in class diagram
MAX_CLASS_METHODS = 7   # Max methods to show in class diagram


# --- Jac-Exportable Functions ---

def function_md(func_data: dict) -> str:
    """
    Generate markdown documentation for a single function.
    
    Args:
        func_data: The dictionary for a function node from the CCG.
        
    Returns:
        A formatted markdown string.
    """
    md = f"#### `{func_data.get('name', 'unnamed_function')}()`\n\n"
    
    if func_data.get('docstring'):
        md += f"```text\n{func_data['docstring']}\n```\n\n"
    
    md += "**Parameters:**\n\n"
    params = func_data.get('params', [])
    if params:
        for p in params:
            md += f"- `{p}`\n"
    else:
        md += "- `None`\n"
    
    md += "\n"
    
    if func_data.get('returns'):
        md += f"**Returns:** `{func_data['returns']}`\n\n"
    
    # Show calls from this function
    calls = func_data.get('calls', [])
    if calls:
        md += f"**Calls:** {', '.join([f'`{c}()`' for c in calls[:5]])}\n\n"
    
    md += f"*Defined in: `{func_data.get('file_path', 'N/A')}` (Line {func_data.get('line', 0)})*\n"
    md += "\n---\n\n"
    return md


def class_md(class_data: dict) -> str:
    """
    Generate markdown documentation for a single class.
    
    Args:
        class_data: The dictionary for a class node from the CCG.
        
    Returns:
        A formatted markdown string.
    """
    md = f"### Class: `{class_data.get('name', 'UnnamedClass')}`\n\n"
    
    if class_data.get('docstring'):
        md += f"```text\n{class_data['docstring']}\n```\n\n"
    
    # Show inheritance
    bases = class_data.get('bases', [])
    if bases:
        md += f"**Inherits from:** {', '.join([f'`{b}`' for b in bases])}\n\n"
    
    # Show attributes
    attributes = class_data.get('attributes', [])
    if attributes:
        md += "**Attributes:**\n\n"
        for attr in attributes:
            md += f"- `{attr}`\n"
        md += "\n"
    
    # Show methods
    methods = class_data.get('methods', [])
    if methods:
        md += "**Methods:**\n\n"
        for method in methods:
            md += f"- `{method}()`\n"
        md += "\n"
    
    md += f"*Defined in: `{class_data.get('file_path', 'N/A')}` (Line {class_data.get('line', 0)})*\n"
    md += "\n---\n\n"
    return md

def ability_md(ability_data: dict) -> str:
    """
    Generate markdown documentation for a Jac ability.
    
    Args:
        ability_data: The dictionary for an ability node from the CCG.
        
    Returns:
        A formatted markdown string.
    """
    ability_type = ability_data.get('ability_type', 'can')
    md = f"#### `{ability_type}: {ability_data.get('name', 'unnamed_ability')}`\n\n"
    
    if ability_data.get('docstring'):
        md += f"```text\n{ability_data['docstring']}\n```\n\n"

    md += f"**Signature:** `{ability_data.get('signature', 'N/A')}`\n\n"
    
    md += f"*Defined in: `{ability_data.get('file_path', 'N/A')}` (Line {ability_data.get('line', 0)})*\n"
    md += "\n---\n\n"
    return md

def walker_md(walker_data: dict) -> str:
    """
    Generate markdown documentation for a Jac walker.
    
    Args:
        walker_data: The dictionary for a walker node from the CCG.
        
    Returns:
        A formatted markdown string.
    """
    md = f"### Walker: `{walker_data.get('name', 'UnnamedWalker')}`\n\n"
    
    if walker_data.get('docstring'):
        md += f"```text\n{walker_data['docstring']}\n```\n\n"

    # Show attributes
    attributes = walker_data.get('attributes', [])
    if attributes:
        md += "**Attributes (has):**\n\n"
        for attr in attributes:
            md += f"- `{attr}`\n"
        md += "\n"
    
    md += f"*Defined in: `{walker_data.get('file_path', 'N/A')}` (Line {walker_data.get('line', 0)})*\n"
    md += "\n---\n\n"
    return md


def generate_mermaid_class_diagram(class_nodes: list) -> str:
    """
    Generate a Mermaid.js class diagram from all class nodes.
    
    Args:
        class_nodes: A list of all node::class objects from the graph.
        
    Returns:
        A markdown string containing the Mermaid diagram.
    """
    if not class_nodes:
        return ""
        
    mermaid = "```mermaid\nclassDiagram\n"
    
    added_classes = set()
    relationships = []

    for c_node in class_nodes:
        class_name = c_node.name
        if class_name in added_classes:
            continue
        
        mermaid += f"    class {class_name} {{\n"
        added_classes.add(class_name)
        
        # Add attributes
        attributes = c_node.attributes or []
        for attr in attributes[:MAX_CLASS_ATTRIBUTES]:
            mermaid += f"        +{attr}\n"
        if len(attributes) > MAX_CLASS_ATTRIBUTES:
            mermaid += f"        +... {len(attributes) - MAX_CLASS_ATTRIBUTES} more\n"

        # Add methods
        methods = c_node.methods or []
        for method in methods[:MAX_CLASS_METHODS]:
            mermaid += f"        +{method}()\n"
        if len(methods) > MAX_CLASS_METHODS:
            mermaid += f"        +... {len(methods) - MAX_CLASS_METHODS} more()\n"
            
        mermaid += "    }\n"
        
        # Store inheritance relationships
        bases = c_node.bases or []
        for base in bases:
            relationships.append(f"    {base} <|-- {class_name}\n")

    # Add all relationships at the end
    mermaid += "\n    ' --- Inheritance ---\n"
    for rel in set(relationships): # Use set to avoid duplicates
        mermaid += rel
            
    mermaid += "```\n\n"
    return mermaid


def generate_mermaid_function_calls(call_edges: list) -> str:
    """
    Generate a Mermaid.js flowchart for function calls.
    
    Args:
        call_edges: A list of all 'calls' edge objects from the graph.
        
    Returns:
        A markdown string containing the Mermaid diagram.
    """
    if not call_edges:
        return "```mermaid\nflowchart TD\n    A[No function calls detected in the graph]\n```\n\n"
        
    mermaid = "```mermaid\nflowchart TD\n"
    
    added_rels = set()
    rel_count = 0
    
    for edge in call_edges:
        if rel_count >= MAX_MERMAID_NODES:
            break
            
        # Get the 'from' (source) and 'to' (target) nodes
        from_node = edge.source
        to_node = edge.target
        
        # Ensure they are function or ability nodes
        if from_node.kind not in ('function', 'ability') or to_node.kind not in ('function', 'ability'):
            continue
            
        from_name = from_node.name.replace('-', '_').replace('.', '_')
        to_name = to_node.name.replace('-', '_').replace('.', '_')
        
        # Create a unique ID for node styling
        from_id = f"f_{from_name}"
        to_id = f"t_{to_name}"
        
        rel_key = (from_id, to_id)
        
        if rel_key not in added_rels:
            mermaid += f"    {from_id}[{from_node.name}()] --> {to_id}[{to_node.name}()]\n"
            added_rels.add(rel_key)
            rel_count += 1
            
    if rel_count == 0:
        mermaid += "    A[No function calls detected in the graph]\n"
    elif rel_count >= MAX_MERMAID_NODES:
        mermaid += f"\n    ... {len(call_edges) - rel_count} more relationships not shown ...\n"

    mermaid += "```\n\n"
    return mermaid

