# ------------------------------
# Core Graph Definitions
# ------------------------------
# Defines all nodes and edges for the Codebase Genius graph.

# --- Graph Structure Nodes ---

node repository {
    has repo_url: str;
    has name: str;
    has local_path: str;
    has readme_summary: dict = {};
    has output_path: str;
}

node folder {
    has name: str;
    has path: str;
}

node file {
    has name: str;
    has path: str;
    has extension: str;
}

# --- Code Context Graph (CCG) Nodes ---
# 'code_file' inherits from 'file'
node code_file: file {
    has lines: int;
    has language: str;
}

# --- CCG Code Element Nodes ---
# These nodes represent elements *inside* a code file

node function {
    has name: str;
    has signature: str;
    has params: list = [];
    has returns: str = "void";
    has docstring: str = "";
    has line_start: int;
    has line_end: int;
}

node class_def {
    has name: str;
    has docstring: str = "";
    has line_start: int;
    has line_end: int;
}

node walker_def {
    has name: str;
    has docstring: str = "";
    has line_start: int;
    has line_end: int;
}

node node_def {
    has name: str;
    has docstring: str = "";
    has line_start: int;
    has line_end: int;
}

node edge_def {
    has name: str;
    has docstring: str = "";
    has line_start: int;
    has line_end: int;
}


# --- Graph Structure Edges ---

edge contains; # Connects repository -> folder/file
             # Connects folder -> folder/file


# --- Code Context Graph (CCG) Edges ---

edge defines; # Connects code_file -> function/class/etc.
             # Connects class_def -> function (for methods)

edge calls;   # Connects function -> function
             # Connects function -> class_def (for instantiation)

edge inherits; # Connects class_def -> class_def

