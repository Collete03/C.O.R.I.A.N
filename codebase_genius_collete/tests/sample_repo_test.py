"""
End-to-end test on a sample repository.

This script tests the complete 3-tier workflow by making an HTTP request
to the running FastAPI server (server.py), which proxies to the 
Jac server (main.jac).

REQUIREMENTS:
1. All 3 servers must be running in separate terminals.
   - jac serve main.jac
   - uvicorn server:app
   - streamlit run frontend/app.py
2. Run this test from the ROOT directory:
   - python tests/sample_repo_test.py
"""

import httpx
import os
import sys
import time
from pathlib import Path

# --- Configuration ---
BASE_API_URL = "http://127.0.0.1:8000"
GENERATE_ENDPOINT = f"{BASE_API_URL}/generate"
DEFAULT_TEST_REPO = "https://github.com/kennethreitz/setup.py"
# ---------------------

def run_e2e_test(repo_url: str):
    """Run the end-to-end test against the running servers."""
    
    print("=" * 70)
    print("  CODEBASE GENIUS - End-to-End Integration Test")
    print("=" * 70)
    print(f"\n  Target API: {BASE_API_URL}")
    print(f"  Target Repo: {repo_url}\n")
    print("  NOTE: Ensure all 3 servers (Jac, Uvicorn, Streamlit) are running!")
    print("-" * 70)

    start_time = time.time()
    
    try:
        # 1. Make the API request to the FastAPI server
        print(f"\n[1/3] Sending POST request to {GENERATE_ENDPOINT}...")
        
        with httpx.Client(timeout=300.0) as client: # 5 minute timeout
            response = client.post(
                GENERATE_ENDPOINT,
                json={"github_url": repo_url, "use_llm": False} # Disable LLM for test speed
            )
        
        duration = time.time() - start_time
        print(f"  ✓ Request complete in {duration:.2f} seconds.")

        # 2. Check the API response
        print(f"\n[2/3] Analyzing API response...")
        if response.status_code != 200:
            print(f"  ✗ TEST FAILED: API returned status {response.status_code}")
            print(f"  Response: {response.text}")
            return 1 # Exit with error

        print(f"  ✓ API Status: {response.status_code}")
        
        response_data = response.json()
        assert response_data['status'] == 'success', "Response 'status' field was not 'success'"
        assert response_data['repo_name'] is not None, "Response did not contain 'repo_name'"
        assert response_data['output_path'] is not None, "Response did not contain 'output_path'"
        
        print("  ✓ API response JSON is valid.")
        
        # 3. Verify the output file
        print(f"\n[3/3] Verifying output file...")
        output_path_str = response_data['output_path']
        output_file = Path(output_path_str)
        
        if not output_file.exists():
            print(f"  ✗ TEST FAILED: Output file not found at path: {output_path_str}")
            return 1
            
        print(f"  ✓ Output file found: {output_path_str}")
        
        # Check file size
        file_size = output_file.stat().st_size
        assert file_size > 100, f"Output file size is too small ({file_size} bytes)"
        print(f"  ✓ File size is valid ({file_size} bytes).")
        
        # Check content
        content = output_file.read_text()
        checks = {
            'Title': f"# {response_data['repo_name']}" in content,
            'Overview': "## Project Overview" in content,
            'File Structure': "## File Structure" in content,
            'Statistics': "### Repository Statistics" in content,
            'API Reference': "## API Reference" in content
        }
        
        print("\n  Content Verification:")
        all_passed = True
        for check_name, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"    {status} Contains '{check_name}' section")
            if not passed:
                all_passed = False
                
        if not all_passed:
            print("\n  ✗ TEST FAILED: Some content checks failed.")
            print("  --- File Content Start ---")
            print(content[:500] + "...")
            print("  --- File Content End ---")
            return 1

        print("\n  ✓ All content checks passed.")
        print("\n" + "=" * 70)
        print("  ✓✓✓ E2E TEST PASSED! ✓✓✓")
        print("=" * 70)
        return 0

    except httpx.ConnectError:
        print("\n  ✗ TEST FAILED: Connection Error")
        print(f"  Could not connect to {BASE_API_URL}.")
        print("  Please ensure the Uvicorn (server.py) and Jac (main.jac) servers are running.")
        return 1
        
    except Exception as e:
        print(f"\n  ✗ TEST FAILED: An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # Allow custom repo URL from command line
    repo_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_TEST_REPO
    
    # Ensure we are running from the root directory
    if not (Path('main.jac').exists() and Path('utils').is_dir()):
        print("Error: This test must be run from the project's root directory.")
        print("Example: python tests/sample_repo_test.py")
        sys.exit(1)

    sys.exit(run_e2e_test(repo_url))

