"""
Basic unit tests for Codebase Genius utility functions.
Ensures that the helper scripts in the `utils/` directory work as expected.

Run with:
- Make sure venv is active: source codebasejac-env/bin/activate
- Run from ROOT directory: pytest tests/test_basic.py
"""

import sys
import os
import pytest
from pathlib import Path

# --- Setup sys.path ---
# This allows the test to import files from the `utils/` directory
# by adding the project's root folder to the Python path.
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
# ---------------------

# Import the utility functions we want to test
from utils.error_handler import is_valid_github_url, handle_clone_error
from utils.readme_parser import find_readme, summarize_readme
from utils.python_parser import parse_file_by_extension, build_code_context_graph

# --- Mock File System ---
# We use pytest 'fixtures' to create temporary files for our tests
# so we don't have to rely on real files.

@pytest.fixture
def temp_py_file(tmp_path):
    """Create a temporary Python file for parsing tests."""
    py_content = """
import os

class MyClass(AnotherClass):
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello, {self.name}")
        self.other_func()

def other_func():
    pass
"""
    file_path = tmp_path / "test_script.py"
    file_path.write_text(py_content)
    return str(file_path)

@pytest.fixture
def temp_jac_file(tmp_path):
    """Create a temporary Jac file for parsing tests."""
    jac_content = """
import:jac from nodes;

walker my_walker {
    has name: str = "JAC";
    can walk_it with entry {
        std.out("Walking");
    }
}

node my_node {
    has data: str;
}

edge my_edge;
"""
    file_path = tmp_path / "test_walker.jac"
    file_path.write_text(jac_content)
    return str(file_path)

@pytest.fixture
def temp_readme_file(tmp_path):
    """Create a temporary README.md file for parsing tests."""
    readme_content = """
# My Test Project

This is the main description. It has several sentences.
This is the second sentence.

## Features
- Feature 1
- Feature 2

## Installation
```bash
pip install my-project
```
This is how you install it.
"""
    file_path = tmp_path / "README.md"
    file_path.write_text(readme_content)
    return str(tmp_path) # Return the directory path

# --- Test Cases ---

def test_github_url_validation():
    """Tests the `is_valid_github_url` function."""
    print("\nTesting GitHub URL Validation...")
    
    # Valid URLs
    assert is_valid_github_url("https://github.com/user/repo")[0] == True
    assert is_valid_github_url("https://github.com/Jaseci-Lab/jaseci")[0] == True
    
    # Invalid URLs
    assert is_valid_github_url("https://gitlab.com/user/repo")[0] == False, "Should reject non-GitHub domains"
    assert is_valid_github_url("https://github.com/user")[0] == False, "Should reject user-only paths"
    assert is_valid_github_url("ftp://github.com/user/repo")[0] == False, "Should reject non-http/s protocols"
    assert is_valid_github_url("not a url")[0] == False, "Should reject non-URLs"
    print("  ✓ URL Validation tests passed.")

def test_readme_parser(temp_readme_file):
    """Tests the `find_readme` and `summarize_readme` functions."""
    print("\nTesting README Parser...")
    
    readme_path = find_readme(temp_readme_file)
    assert readme_path is not None, "Should find the README.md file"
    assert Path(readme_path).name == "README.md"
    
    summary = summarize_readme(readme_path)
    assert summary['title'] == "My Test Project", "Should extract correct title"
    assert "This is the main description" in summary['summary'], "Should extract summary"
    assert "pip install my-project" in summary['installation'], "Should extract installation block"
    print("  ✓ README Parser tests passed.")

def test_python_parser(temp_py_file):
    """Tests the `parse_file_by_extension` for a .py file."""
    print("\nTesting Python Parser...")
    
    data = parse_file_by_extension(temp_py_file)
    
    assert 'error' not in data, "Should parse without errors"
    assert len(data['classes']) == 1, "Should find 1 class"
    assert data['classes'][0]['name'] == "MyClass"
    assert data['classes'][0]['bases'] == ["AnotherClass"], "Should find base class"
    
    assert len(data['functions']) == 2, "Should find 2 functions (greet, other_func)"
    assert data['functions'][0]['name'] == "greet"
    assert data['functions'][0]['parent_class'] == "MyClass", "Should assign parent class"
    
    assert len(data['relationships']) == 2, "Should find 2 relationships (inherits, calls)"
    assert data['relationships'][0]['type'] == 'inherits'
    assert data['relationships'][1]['type'] == 'calls'
    print("  ✓ Python Parser tests passed.")

def test_jac_parser(temp_jac_file):
    """Tests the `parse_file_by_extension` for a .jac file."""
    print("\nTesting Jac Parser...")
    
    data = parse_file_by_extension(temp_jac_file)
    
    assert 'error' not in data, "Should parse without errors"
    assert len(data['walkers']) == 1, "Should find 1 walker"
    assert data['walkers'][0]['name'] == "my_walker"
    
    assert len(data['nodes']) == 1, "Should find 1 node"
    assert data['nodes'][0]['name'] == "my_node"
    
    assert len(data['edges']) == 1, "Should find 1 edge"
    assert data['edges'][0]['name'] == "my_edge"
    
    assert len(data['imports']) == 1, "Should find 1 import"
    print("  ✓ Jac Parser tests passed.")

def test_unsupported_file_parser(tmp_path):
    """Tests the parser on an unsupported file type."""
    print("\nTesting Unsupported File Parser...")
    
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Hello")
    
    data = parse_file_by_extension(str(txt_file))
    
    assert 'error' in data, "Should return an error"
    assert "Unsupported file type" in data['error']
    print("  ✓ Unsupported file parser test passed.")

def test_ccg_builder(temp_py_file, temp_jac_file):
    """Tests the `build_code_context_graph` function."""
    print("\nTesting CCG Builder...")
    
    py_data = parse_file_by_extension(temp_py_file)
    jac_data = parse_file_by_extension(temp_jac_file)
    
    ccg = build_code_context_graph([py_data, jac_data])
    
    assert "MyClass" in ccg['classes'], "CCG should contain Python classes"
    assert "greet" in ccg['functions'], "CCG should contain Python functions"
    assert "my_walker" in ccg['walkers'], "CCG should contain Jac walkers"
    assert "my_node" in ccg['nodes'], "CCG should contain Jac nodes"
    
    assert len(ccg['relationships']) == 2, "CCG should aggregate relationships"
    print("  ✓ CCG Builder tests passed.")

