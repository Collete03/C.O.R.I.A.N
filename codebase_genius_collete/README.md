C.O.R.I.A.N (Codebase Genius)

Welcome to Codebase Genius, an AI-powered documentation generator. This tool analyzes any GitHub repository, understands its file structure and code, and produces a comprehensive, multi-format documentation report.

This project consists of two main parts:

The Jac Engine (Backend): A powerful analysis pipeline built with jaseci.

The Streamlit UI (Frontend): A user-friendly web interface to run the engine.

✨ Features

Repository Mapper (repo-mapper.jac): Clones any public GitHub repository and maps its entire file structure into a graph.

Code Analyzer (code_analyzer.jac): Parses source files (.py, .jac) to build a Code Context Graph (CCG), identifying functions, classes, walkers, and their relationships (calls, inherits).

Documentation Genie (doc_genie.jac): Walks the completed graph to generate a beautiful Markdown report, including statistics, API references, and Mermaid diagrams.

Streamlit Frontend (frontend/app.py): A polished, easy-to-use web UI to input a repo URL and view results.

FastAPI Backend (main.py): The missing link! A Python server that connects the frontend to the Jac engine.

📦 Installation

Clone the repository:

git clone <your-repo-url>
cd codebase_genius_collete


Install dependencies:
This project has Python dependencies for both the backend and frontend.

pip install -r requirements.txt


▶️ How to Run

You must run the Backend and Frontend in two separate terminal windows.

1. Run the Backend Server

In your first terminal, start the FastAPI server:

uvicorn server:app --reload


You should see a message that the server is running on http://localhost:8000.

2. Run the Frontend App

In your second terminal, start the Streamlit frontend:

streamlit run frontend/app.py


This will automatically open the web application in your browser (usually at http://localhost:8501). You can now paste a GitHub URL and generate documentation!

Meta-Documentation

This project also includes a script to generate documentation about itself.

Generating This Project's Own Report

The documentation_pipeline.py script will analyze the .jac and .py files in this project (not a remote one) and combine it with this project's own Git history.

# Run this from the project's root directory
python documentation_pipeline.py


This will create a new directory named C.O.R.I.A.N_documentation containing a detailed report on the "Codebase Genius" project itself.

📁 Project Structure

Here is the detailed project structure based on your screenshots:

/
├── agents/
│   ├── code_analyzer.jac
│   ├── doc_genie.jac
│   └── repo_mapper.jac
│
├── C.O.R.I.A.N_documentation/  # Output of the self-documentation pipeline
├── codebasejac-env/            # Python virtual environment
│
├── frontend/
│   ├── app.py                  # The Streamlit frontend UI
│   ├── app.py.backup
│   └── README.md               # Frontend-specific instructions
│
├── outputs/                    # Default folder for generated reports
├── repos/                      # Default folder for cloned repos
│
├── tests/
│   ├── README.md
│   ├── sample_repo_test.py
│   ├── test_api_sh.py
│   ├── test_api.py
│   └── test_basic.py
│
├── utils/
│   ├── __init__.py
│   ├── error_handler.py
│   ├── file_tree.py
│   ├── git_helper.py
│   ├── llm_helper.py
│   ├── markdown_generator.py
│   ├── python_parser.py
│   └── readme_parser.py
│
├── .env
├── .env.example
├── .gitignore
├── documentation_pipeline.py   # Meta-script to document THIS project
├── main.py                     # FastAPI backend server (for jaseci)
├── nodes.jac                   # Core graph node/edge definitions
├── py_bridge.py                # Python helpers for Jac
├── requirements.txt            # All Python dependencies
├── server.py                   # (Another server file, check which is used)
└── README.md                   
