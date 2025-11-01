"""
Git Helper Utility.

Provides functions to clone a remote Git repository using the GitPython library.
Includes functionality to safely remove an existing repository before cloning.
"""

import os
import shutil
from git import Repo, exc

def safe_clone(url: str, dest: str) -> tuple[bool, str]:
    """
    Clones a repository, removing the destination folder if it already exists.
    
    Args:
        url: The remote Git repository URL.
        dest: The local directory path to clone into.
        
    Returns:
        A tuple of (success: bool, result: str).
        On success, result is the destination path.
        On failure, result is the error message.
    """
    try:
        # --- 1. Remove Existing Directory ---
        # This ensures we always get a fresh clone and avoid conflicts.
        if os.path.exists(dest):
            print(f"  > Removing existing directory: {dest}")
            # Use shutil.rmtree for robust directory removal
            # Add error handling for Windows file lock issues if necessary
            try:
                shutil.rmtree(dest)
            except PermissionError:
                return (
                    False, 
                    "PermissionError: Could not remove old repo. "
                    "Please check file permissions or close open files."
                )

        # --- 2. Clone the Repository ---
        # Repo.clone_from will create the destination directory.
        Repo.clone_from(url, dest)
        
        return True, dest

    except exc.GitCommandError as e:
        # This catches errors from the git command itself,
        # like "repository not found" or "permission denied".
        return False, str(e)
    
    except Exception as e:
        # Catch any other unexpected errors (e.g., OS-level issues)
        return False, f"An unexpected error occurred during clone: {str(e)}"

