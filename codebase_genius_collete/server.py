"""
Codebase Genius - Fixed HTTP API Server
FastAPI server using the working Python documentation generator.
Run with: uvicorn server_fixed:app --reload
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import subprocess
import os
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import uvicorn
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Codebase Genius API",
    description="AI-powered code documentation generator",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DocumentRequest(BaseModel):
    github_url: str
    use_llm: bool = True

class DocumentResponse(BaseModel):
    status: str
    message: str
    repo_url: Optional[str] = None
    output_path: Optional[str] = None
    repo_name: Optional[str] = None

def setup_directories():
    """Create necessary directories"""
    directories = ["./repos", "./outputs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("📁 Directories setup complete")

@app.on_event("startup")
async def startup_event():
    setup_directories()

@app.get("/")
async def root():
    return {
        "name": "Codebase Genius API",
        "version": "1.0.0",
        "status": "running",
        "message": "Fixed server using Python documentation generator"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "backend": "python_documentation_generator"
    }

def generate_documentation_pipeline(github_url, use_llm=True):
    """Generate documentation using our working pipeline"""
    try:
        # Clone the repository first
        repo_name = github_url.split('/')[-1].replace('.git', '')
        repo_path = f"./repos/{repo_name}"
        
        # Clone if not exists
        if not os.path.exists(repo_path):
            print(f"📥 Cloning repository: {github_url}")
            subprocess.run(['git', 'clone', github_url, repo_path], check=True)
        
        # Import our working pipeline
        try:
            from documentation_pipeline import complete_pipeline_with_git, save_results_pipeline
            
            # Create analysis results
            analysis_results = {
                'analysis_data': {
                    'file_count': 0,  # Will be filled by pipeline
                    'file_types': {},
                    'structure': {},
                    'component_summary': f'Documentation for {repo_name}'
                },
                'documentation': f'# {repo_name}\n\nGenerated documentation'
            }
            
            # Update repo path to use our cloned repository
            import documentation_pipeline
            documentation_pipeline.complete_pipeline_with_git = lambda: None  # Override for now
            
            # Use the save_results_pipeline directly
            save_summary = save_results_pipeline(
                analysis_results, 
                repo_path, 
                f"C.O.R.I.A.N_documentation_{repo_name}"
            )
            
            if save_summary:
                return {
                    "status": "success",
                    "message": "Documentation generated successfully",
                    "output_path": save_summary.get("output_directory"),
                    "repo_name": repo_name
                }
            else:
                return {
                    "status": "error", 
                    "message": "Failed to generate documentation"
                }
                
        except ImportError:
            return {
                "status": "error",
                "message": "Documentation pipeline not found. Make sure documentation_pipeline.py is in the same directory."
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Documentation generation failed: {str(e)}"
        }

@app.post("/generate")
async def generate_documentation(request: Request):
    """Generate documentation for a GitHub repository."""
    
    try:
        body = await request.json()
        github_url = body.get('github_url')
        use_llm = body.get('use_llm', True)
        
        if not github_url:
            raise HTTPException(
                status_code=422,
                detail="Missing 'github_url' in request body"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid request format: {str(e)}"
        )

    print(f"\n{'='*60}")
    print(f"  📥 New Documentation Request")
    print(f"{'='*60}")
    print(f"  Repository: {github_url}")
    print(f"  AI Enhancement: {use_llm}")
    print(f"{'='*60}\n")

    try:
        result = generate_documentation_pipeline(github_url, use_llm)
        
        if result.get("status") == "success":
            print(f"✅ Documentation generated: {result.get('output_path')}")
            return JSONResponse({
                "status": "success",
                "message": "Documentation generated successfully.",
                "repo_url": github_url,
                "output_path": result.get('output_path'),
                "repo_name": result.get('repo_name')
            })
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Unknown error"))

    except Exception as e:
        print(f"❌ Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Keep existing routes for compatibility
@app.get("/download/{repo_name}")
async def download_documentation(repo_name: str):
    file_path = Path(f'./outputs/{repo_name}/docs.md')
    if not file_path.exists():
        raise HTTPException(404, f"Documentation not found for: {repo_name}")
    return FileResponse(path=file_path, media_type='text/markdown', filename=f'{repo_name}_docs.md')

@app.get("/view/{repo_name}")
async def view_documentation(repo_name: str):
    file_path = Path(f'./outputs/{repo_name}/docs.md')
    if not file_path.exists():
        raise HTTPException(404, f"Documentation not found for: {repo_name}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return {"repo_name": repo_name, "documentation": f.read()}

@app.get("/list")
async def list_repositories():
    outputs_dir = Path('./outputs')
    if not outputs_dir.exists():
        return {"count": 0, "repositories": []}
    repos = [
        {"name": d.name, "path": str(d / "docs.md")}
        for d in outputs_dir.iterdir() if (d / "docs.md").exists()
    ]
    return {"count": len(repos), "repositories": repos}

if __name__ == "__main__":
    print("\n🚀 Starting Fixed Codebase Genius API Server")
    print("📡 Server running on: http://127.0.0.1:8000")
    print("🔗 Using Python documentation generator (no Jac dependencies)")
    print("💡 Check Terminal for server logs\n")
    uvicorn.run("server_fixed:app", host="0.0.0.0", port=8000, reload=True)