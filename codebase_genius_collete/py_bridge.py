# Add to your existing py_bridge.py
from error_handler import handle_clone_error, is_valid_github_url

def py_handle_clone_error(url: str, error_msg: str) -> str:
    """Jac-accessible function to handle clone errors"""
    class MockError:
        def __init__(self, msg):
            self.msg = msg
        def __str__(self):
            return self.msg
    
    return handle_clone_error(url, MockError(error_msg))

def py_is_valid_github_url(url: str) -> dict:
    """Jac-accessible function to validate GitHub URLs"""
    is_valid, error = is_valid_github_url(url)
    return {"is_valid": is_valid, "error": error}