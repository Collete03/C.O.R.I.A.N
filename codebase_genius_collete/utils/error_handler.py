"""
Error handling utilities for Codebase Genius.
Provides custom exception classes and graceful error handling
for common failures, such as cloning or URL validation.
"""

# --- Custom Exception Classes ---

class CodebaseGeniusError(Exception):
    """Base exception for all Codebase Genius errors."""
    pass


class InvalidURLError(CodebaseGeniusError):
    """Raised when GitHub URL is invalid or malformed."""
    pass


class CloneError(CodebaseGeniusError):
    """Raised when repository cloning fails for any reason."""
    pass


class ParsingError(CodebaseGeniusError):
    """Raised when code parsing (AST or regex) fails."""
    pass


class DocumentationError(CodebaseGeniusError):
    """Raised when documentation generation or file writing fails."""
    pass


# --- Helper Functions (Imported by Jac) ---

def handle_clone_error(url: str, error: Exception) -> str:
    """
    Analyzes a cloning exception and returns a user-friendly message.
    
    Args:
        url: The repository URL that failed to clone.
        error: The raw Exception object.
        
    Returns:
        A formatted, user-friendly error string.
    """
    error_str = str(error).lower()
    
    if 'not found' in error_str or '404' in error_str:
        return (
            f"Repository not found: {url}. Please check if the URL is "
            "correct and the repository exists and is public."
        )
    
    elif 'permission' in error_str or 'authentication' in error_str or '403' in error_str:
        return (
            f"Access denied: {url}. This repository may be private "
            "or require authentication credentials."
        )
    
    elif 'network' in error_str or 'connection' in error_str:
        return (
            "Network error: Unable to connect to GitHub. "
            "Please check your internet connection."
        )
    
    elif 'timeout' in error_str:
        return (
            "Timeout error: The repository took too long to clone. "
            "It may be very large."
        )
    
    else:
        # Fallback for other Git errors
        return f"Clone failed for {url}. Details: {str(error)}"


def is_valid_github_url(url: str) -> tuple[bool, str | None]:
    """
    Validate GitHub URL format.
    
    Args:
        url: The GitHub repository URL string.
        
    Returns:
        A tuple of (is_valid: bool, error_message: str or None).
    """
    import re
    
    if not url:
        return False, "URL is empty"
    
    # Standard pattern: https://github.com/user/repo
    # Allows for . or - in user/repo names
    pattern = r'^https?://github\.com/[\w.-]+/[\w.-]+/?$'
    
    # Strip trailing .git if present (for matching)
    url_to_check = url.removesuffix('.git')
    
    if not re.match(pattern, url_to_check):
        return (
            False, 
            "Invalid GitHub URL format. "
            "Expected: https://github.com/username/repository"
        )
    
    return True, None