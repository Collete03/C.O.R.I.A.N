# main.py - Python Orchestrator (replaces main.jac)
import subprocess
import os
import json
from pathlib import Path

def run_jac_agent(agent_file, env_vars=None):
    """Run a Jac agent and return the result"""
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    
    try:
        result = subprocess.run(
            ['jac', 'run', agent_file],
            capture_output=True,
            text=True,
            timeout=300,
            env=env,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            # Try to parse JSON output from Jac
            try:
                output = json.loads(result.stdout.strip())
                return {"success": True, "data": output}
            except:
                return {"success": True, "output": result.stdout}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_documentation(github_url, use_llm=True):
    """Main pipeline orchestrator - replaces main.jac walker"""
    print("🚀 Starting Codebase Genius Pipeline...")
    
    # Extract repo name
    repo_name = github_url.rstrip('/').split('/')[-1].replace('.git', '')
    output_path = f"./outputs/{repo_name}/docs.md"
    
    # Ensure output directory exists
    Path(f"./outputs/{repo_name}").mkdir(parents=True, exist_ok=True)
    
    # Step 1: Repository Mapping
    print("📁 Step 1/5: Repository Mapping...")
    map_result = run_jac_agent(
        "repo_mapper.jac",
        {"GITHUB_URL": github_url, "REPO_NAME": repo_name, "USE_LLM": str(use_llm).lower()}
    )
    
    if not map_result["success"]:
        return {"status": "error", "message": f"Repo mapping failed: {map_result['error']}"}
    
    # Step 2: Code Analysis
    print("🔍 Step 2/5: Code Analysis...")
    analysis_result = run_jac_agent(
        "code_analyzer.jac", 
        {"GITHUB_URL": github_url, "REPO_NAME": repo_name, "USE_LLM": str(use_llm).lower()}
    )
    
    if not analysis_result["success"]:
        return {"status": "error", "message": f"Code analysis failed: {analysis_result['error']}"}
    
    # Step 3: Documentation Generation
    print("📝 Step 3/5: Documentation Generation...")
    doc_result = run_jac_agent(
        "doc_genie.jac",
        {"GITHUB_URL": github_url, "REPO_NAME": repo_name, "USE_LLM": str(use_llm).lower()}
    )
    
    if not doc_result["success"]:
        return {"status": "error", "message": f"Documentation generation failed: {doc_result['error']}"}
    
    # Step 4: Verify output
    if Path(output_path).exists():
        print("✅ Pipeline completed successfully!")
        return {
            "status": "success",
            "message": "Documentation generated successfully",
            "output_path": output_path,
            "repo_name": repo_name
        }
    else:
        return {"status": "error", "message": "Pipeline completed but output file not found"}

# For direct testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        github_url = sys.argv[1]
        use_llm = len(sys.argv) > 2 and sys.argv[2].lower() == "true"
        result = generate_documentation(github_url, use_llm)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python main.py <github_url> [use_llm]")
        print("Example: python main.py https://github.com/username/repo true")