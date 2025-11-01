"""
README Parser Utility.

Finds and parses the README.md file from a repository to extract:
- Title
- A short summary (first few sentences of the description)
- Installation instructions (if found)
- Key features (if found)

This provides the initial context for the documentation.
"""

import os
import re
from typing import Dict, Any, Optional

def find_readme(repo_path: str) -> Optional[str]:
    """
    Find the main README file in the repository root.
    
    Args:
        repo_path: The local path to the cloned repository.
        
    Returns:
        The full path to the README file, or None if not found.
    """
    # Common README filenames, ordered by preference
    readme_names = [
        'README.md', 'README.MD', 'Readme.md', 'readme.md', 
        'README.rst', 'README.txt', 'README'
    ]
    
    for name in readme_names:
        readme_path = os.path.join(repo_path, name)
        if os.path.exists(readme_path):
            return readme_path
            
    # Check one level deeper (e.g., in a 'docs' folder or src folder)
    for root, dirs, files in os.walk(repo_path):
        # Prune search depth
        if root.count(os.sep) - repo_path.count(os.sep) > 2:
            dirs[:] = [] # Don't go deeper than 2 levels
            continue
            
        for name in readme_names:
            if name in files:
                return os.path.join(root, name)
                
    return None


def summarize_readme(readme_path: str, max_sentences=5) -> Dict[str, Any]:
    """
    Summarize README file into key points using regex.
    
    Args:
        readme_path: The full path to the README file.
        max_sentences: The number of sentences to extract for the summary.
        
    Returns:
        A dictionary containing title, summary, and other extracted sections.
    """
    if not readme_path or not os.path.exists(readme_path):
        return {
            'title': 'No README found',
            'summary': 'No README file found in repository.'
        }
    
    try:
        with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # --- Extract Title ---
        # Look for the first H1 heading
        title_match = re.search(r'^\s*#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            # Fallback to the repository folder name
            title = os.path.basename(os.path.dirname(readme_path))
            
        # Clean title (remove badges, etc.)
        title = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', title).strip() # Remove badges

        # --- Extract Description (Summary) ---
        # Find text after the title but before the next H2 heading or major separator
        desc_match = re.search(
            r'^\s*#\s+.+\n+([\s\S]+?)(?=\n\s*(?:##|---|\*\*\*))', 
            content, 
            re.MULTILINE
        )
        
        if desc_match:
            description = desc_match.group(1).strip()
        else:
            # Fallback: just take the first few non-empty lines
            lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
            description = ' '.join(lines[:max_sentences * 2]) # Grab a chunk of text
            
        # Clean the description
        description = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', description) # Remove links, keep text
        description = re.sub(r'[*_`#]', '', description)  # Remove basic markdown formatting
        description = re.sub(r'\s+', ' ', description) # Normalize whitespace
        
        # Truncate to max sentences
        sentences = re.split(r'([.!?])\s+', description) # Split and keep delimiters
        summary_sentences = []
        if len(sentences) > 1:
            for i in range(0, min(len(sentences) - 1, max_sentences * 2), 2):
                summary_sentences.append(sentences[i] + sentences[i+1])
            summary = ' '.join(summary_sentences)
        else:
            summary = sentences[0][:300] # Hard truncate if no sentences found

        if not summary:
            summary = "No summary available."
            
        # --- Extract Installation Section ---
        install_match = re.search(
            r'(^|\n)\s*##?\s+(Install(?:ation)?|Setup|Getting Started)\s*\n([\s\S]+?)(?=\n\s*##?|$)', 
            content, 
            re.DOTALL | re.IGNORECASE
        )
        installation = install_match.group(3).strip() if install_match else None
        
        return {
            'title': title,
            'summary': summary.strip(),
            'installation': installation[:500] if installation else None, # Limit length
        }
    
    except Exception as e:
        return {
            'title': 'Error reading README',
            'summary': f'Failed to parse README: {str(e)}',
            'installation': None
        }
