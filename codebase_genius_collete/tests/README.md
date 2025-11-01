Codebase Genius - Test Suite

This directory contains tests for the Codebase Genius system.

Test Files

1. test_basic.py

Unit tests for individual Python components in the utils/ directory:

URL validation (error_handler.py)

Python file parsing (python_parser.py)

Jac file parsing (python_parser.py)

CCG data building (python_parser.py)

README parsing (readme_parser.py)

Run with:

# Make sure your venv is active
pytest tests/test_basic.py -v


2. sample_repo_test.py

End-to-end integration test:

Tests the complete 3-tier workflow (Streamlit -> FastAPI -> Jac Server).

Clones a real repository (https://github.com/kennethreitz/setup.py).

Verifies that a docs.md file is successfully generated.

Checks the docs.md for key sections (Title, File Structure, etc.).

Run with:

# Make sure all 3 servers are running first!
# (jac serve, uvicorn, streamlit)
# Then, in a 4th terminal:
python tests/sample_repo_test.py


Running All Tests

You can run all tests at once using pytest.

# Make sure your venv is active
pytest -v


Troubleshooting

ImportError

Make sure you have activated your virtual environment (source codebasejac-env/bin/activate) and are running the tests from the root directory (codebase_genius_final/), not from inside the tests/ directory.

Jac Not Found

This means your environment isn't active. Run source codebasejac-env/bin/activate.

Test Failures

Ensure all dependencies are installed: pip install -r requirements.txt.

For sample_repo_test.py, ensure all three servers are running in separate terminals before you run the test.