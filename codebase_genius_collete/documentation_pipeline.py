import os
import json
import datetime
import markdown
from pathlib import Path
import subprocess
import shutil
import traceback

class GitIntegratedDocumentationSaver:
    def __init__(self, output_dir="documentation_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        print(f"📚 Documentation output directory set to: {self.output_dir.resolve()}")

    def extract_git_documentation(self, repo_path):
        """Extract built-in Git documentation and metadata"""
        print("🔍 Extracting Git documentation and metadata...")
        
        git_info = {}
        repo_path = Path(repo_path)
        
        if not (repo_path / ".git").is_dir():
            print(f"⚠️  WARNING: '{repo_path.resolve()}' does not appear to be a git repository.")
            return {"error": "Not a git repository or .git directory not found."}

        try:
            # Get README if exists
            readme_content = self._get_readme(repo_path)
            
            # Get Git history and contributors
            git_history = self._get_git_history(repo_path)
            
            # Get recent commits
            recent_commits = self._get_recent_commits(repo_path)
            
            # Get file change statistics
            file_stats = self._get_file_statistics(repo_path)
            
            git_info = {
                "readme": readme_content,
                "git_history": git_history,
                "recent_commits": recent_commits,
                "file_statistics": file_stats,
                "branches": self._get_branches(repo_path),
                "tags": self._get_tags(repo_path)
            }
            print("✅ Git documentation extraction successful.")
        except Exception as e:
            print(f"⚠️  Could not extract Git info: {e}")
            git_info = {"error": str(e)}
            
        return git_info
    
    def _get_readme(self, repo_path):
        """Extract README content"""
        readme_files = ['README.md', 'README.rst', 'README.txt', 'README']
        for readme_file in readme_files:
            readme_path = repo_path / readme_file
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
                except Exception as e:
                    print(f"⚠️  Could not read {readme_file}: {e}")
        return "No README found"
    
    def _get_git_history(self, repo_path):
        """Get Git history summary"""
        try:
            result = subprocess.run(
                ['git', 'log', '--oneline', '--decorate', '--all', '-n', '50'],
                cwd=repo_path, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='ignore'
            )
            return result.stdout if result.returncode == 0 else "Git history unavailable"
        except Exception as e:
            print(f"⚠️  Git history extraction failed: {e}")
            return "Git history extraction failed"
    
    def _get_recent_commits(self, repo_path, count=10):
        """Get recent commits with details"""
        try:
            result = subprocess.run([
                'git', 'log', f'-{count}', '--pretty=format:%h|%an|%ad|%s',
                '--date=short'
            ], cwd=repo_path, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='ignore')
            
            commits = []
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|', 3)
                        if len(parts) == 4:
                            commits.append({
                                'hash': parts[0],
                                'author': parts[1],
                                'date': parts[2],
                                'message': parts[3]
                            })
            return commits
        except Exception as e:
            print(f"⚠️  Recent commits extraction failed: {e}")
            return []
    
    def _get_file_statistics(self, repo_path):
        """Get file change statistics"""
        try:
            # Get most changed files
            result = subprocess.run([
                'git', 'log', '--pretty=format:', '--name-only', '--since="1 year ago"'
            ], cwd=repo_path, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                file_counts = {}
                for file in files:
                    if file.strip():
                        file_counts[file] = file_counts.get(file, 0) + 1
                
                # Sort by frequency
                return dict(sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        except Exception as e:
            print(f"⚠️  File statistics extraction failed: {e}")
            return {}
        
        return {}
    
    def _get_branches(self, repo_path):
        """Get branch information"""
        try:
            result = subprocess.run([
                'git', 'branch', '-a'
            ], cwd=repo_path, capture_output=True, text=True, timeout=10, encoding='utf-8', errors='ignore')
            
            return result.stdout if result.returncode == 0 else "Branch info unavailable"
        except Exception as e:
            print(f"⚠️  Branch extraction failed: {e}")
            return "Branch extraction failed"
    
    def _get_tags(self, repo_path):
        """Get tag information"""
        try:
            result = subprocess.run([
                'git', 'tag', '--list'
            ], cwd=repo_path, capture_output=True, text=True, timeout=10, encoding='utf-8', errors='ignore')
            
            tags = result.stdout.strip().split('\n') if result.returncode == 0 else []
            return [tag for tag in tags if tag]
        except Exception as e:
            print(f"⚠️  Tag extraction failed: {e}")
            return []

    def save_markdown_documentation(self, content, filename="comprehensive_documentation.md"):
        """Save comprehensive documentation as markdown"""
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Comprehensive documentation saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Failed to save markdown: {e}")
            return None

    def save_html_documentation(self, markdown_content, filename="comprehensive_documentation.html"):
        """Convert markdown to HTML and save"""
        try:
            html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
            
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>C.O.R.I.A.N - Comprehensive Documentation</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; margin: 0 auto; padding: 20px; max-width: 1200px; }}
                    code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: "Courier New", Courier, monospace; }}
                    pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    details {{ background: #fafafa; border: 1px solid #eee; border-radius: 5px; margin: 10px 0; }}
                    summary {{ padding: 10px; font-weight: bold; cursor: pointer; }}
                    pre, .git-info {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            print(f"✅ HTML documentation saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Failed to save HTML: {e}")
            return None

    def save_json_metadata(self, enhanced_results, filename="enhanced_analysis_metadata.json"):
        """Save enhanced analysis metadata as JSON"""
        try:
            metadata = {
                "project_name": "C.O.R.I.A.N",
                "analysis_date": datetime.datetime.now().isoformat(),
                "file_count": enhanced_results.get('analysis_data', {}).get('file_count', 0),
                "structure": enhanced_results.get('analysis_data', {}).get('structure', {}),
                "git_integration": {
                    "has_readme": bool(enhanced_results.get('git_documentation', {}).get('readme', '').lower() != 'no readme found'),
                    "recent_commits_count": len(enhanced_results.get('git_documentation', {}).get('recent_commits', [])),
                    "active_files_count": len(enhanced_results.get('git_documentation', {}).get('file_statistics', {}))
                }
            }
            
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"✅ Enhanced metadata saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Failed to save JSON metadata: {e}")
            return None

    def save_repository_structure(self, repo_path, filename="repository_structure.txt"):
        """Save repository file structure"""
        try:
            structure = self._get_repository_structure(repo_path)
            
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(structure)
            
            print(f"✅ Repository structure saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Failed to save repository structure: {e}")
            return None

    def create_readme(self, filename="README.md"):
        """Create a README for the documentation output"""
        readme_content = f"""
# Documentation Output - C.O.R.I.A.N

This directory contains comprehensive automatically generated documentation for the C.O.R.I.A.N project.

## Files:

- `comprehensive_documentation.md` - Main documentation in markdown format
- `comprehensive_documentation.html` - HTML version of documentation
- `enhanced_analysis_metadata.json` - Analysis metadata with Git integration
- `repository_structure.txt` - Repository file structure
- `git_metadata.json` - Raw Git documentation and history
- `generation_summary.json` - Generation process summary

## Features:

- ✅ Code analysis results
- ✅ Git history and metadata
- ✅ Repository structure
- ✅ Recent commit activity
- ✅ File change statistics
- ✅ Built-in README extraction

## Generated on:
{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Usage:
Open `comprehensive_documentation.html` in your browser for the best reading experience.
"""
        
        try:
            filepath = self.output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print(f"✅ Output README saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Failed to save output README: {e}")
            return None

    def _get_repository_structure(self, startpath):
        """Generate directory structure string"""
        structure = []
        startpath = Path(startpath)
        
        # Use Path.glob for a more modern and robust iteration
        for path in sorted(startpath.rglob('*')):
            # Skip .git and other common ignored directories
            if any(part.startswith('.') for part in path.parts) or \
               '__pycache__' in path.parts or \
               'node_modules' in path.parts:
                continue
                
            if path.is_dir():
                level = len(path.relative_to(startpath).parts)
                indent = '  ' * (level - 1)
                structure.append(f"{indent}📂 {path.name}/")
            elif path.is_file():
                level = len(path.relative_to(startpath).parts)
                indent = '  ' * (level - 1)
                structure.append(f"{indent}📄 {path.name}")
                
        # A simpler os.walk version (as you had)
        # for root, dirs, files in os.walk(startpath):
        #     # Skip .git directory and other common ignores
        #     dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        #     files = [f for f in files if not f.startswith('.')]
            
        #     if '.git' in root.split(os.sep):
        #         continue
                
        #     level = root.replace(str(startpath), '').count(os.sep)
        #     indent = ' ' * 2 * level
        #     structure.append(f"{indent}📂 {os.path.basename(root)}/")
        #     subindent = ' ' * 2 * (level + 1)
        #     for file in files:
        #         structure.append(f"{subindent}📄 {file}")
        
        return '\n'.join(structure)

def generate_comprehensive_documentation(enhanced_results):
    """Generate documentation combining analysis and Git data"""
    
    git_info = enhanced_results.get('git_documentation', {})
    analysis_data = enhanced_results.get('analysis_data', {})
    
    # Helper to format recent commits into a markdown table
    def format_commits(commits):
        if not commits:
            return "No recent commits found.\n"
        lines = ["| Hash | Author | Date | Message |",
                 "|---|---|---|---|"]
        for commit in commits:
            # Clean message for table
            message = commit['message'].replace('|', '\|').replace('\n', ' ')
            lines.append(f"| {commit['hash']} | {commit['author']} | {commit['date']} | {message} |")
        return "\n".join(lines) + "\n"

    # Helper to format file stats into a markdown table
    def format_file_stats(stats):
        if not stats:
            return "No file statistics available.\n"
        lines = ["| File | Change Count (Last Year) |",
                 "|---|---|"]
        for file, count in stats.items():
            lines.append(f"| `{file}` | {count} |")
        return "\n".join(lines) + "\n"

    documentation = f"""
# C.O.R.I.A.N - Comprehensive Documentation
Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Project Overview
{analysis_data.get('component_summary', 'No component summary available.')}

### Analysis Summary
- **Total Files Analyzed (Mock Data):** {analysis_data.get('file_count', 'N/A')}
- **File Types (Mock Data):** `{json.dumps(analysis_data.get('file_types', {}))}`

## 2. Repository Information

### 2.1. Built-in README
<details>
<summary>Click to expand/collapse README</summary>

```
{git_info.get('readme', 'No README found.')}
```
</details>

### 2.2. Recent Commits
{format_commits(git_info.get('recent_commits', []))}

### 2.3. Most Active Files (Last Year)
{format_file_stats(git_info.get('file_statistics', {}))}

### 2.4. Branches
<pre>
{git_info.get('branches', 'No branch info available.')}
</pre>

### 2.5. Tags
<pre>
{git_info.get('tags', 'No tags found.')}
</pre>

## 3. Code Structure (Mock Data)
This structure is from the mock analysis data, not the full repository scan.
<pre>
{json.dumps(analysis_data.get('structure', {}), indent=2)}
</pre>
"""
    return documentation

def save_results_pipeline(analysis_results, repo_path, output_dir="documentation_output"):
    """
    Runs the full documentation extraction and saving pipeline.
    This function was created to fix the original script.
    """
    print(f"🚀 Starting documentation pipeline for repo at {repo_path}")
    print(f"📦 Output will be saved to {output_dir}")
    
    saver = GitIntegratedDocumentationSaver(output_dir=output_dir)
    
    # 1. Extract Git documentation
    git_info = saver.extract_git_documentation(repo_path)
    
    if "error" in git_info:
        print(f"❌ Halting pipeline due to error in Git extraction: {git_info['error']}")
        return None
    
    # 2. Combine with analysis results
    enhanced_results = {
        "analysis_data": analysis_results.get('analysis_data', {}),
        "git_documentation": git_info
    }
    
    # 3. Generate comprehensive markdown
    print("📝 Generating comprehensive markdown...")
    comprehensive_md = generate_comprehensive_documentation(enhanced_results)
    
    # 4. Save all artifacts
    md_path = saver.save_markdown_documentation(comprehensive_md)
    html_path = saver.save_html_documentation(comprehensive_md)
    meta_path = saver.save_json_metadata(enhanced_results)
    struct_path = saver.save_repository_structure(repo_path)
    readme_path = saver.create_readme()
    
    # 5. Save raw git_info (as mentioned in create_readme)
    git_meta_path = saver.output_dir / "git_metadata.json"
    try:
        with open(git_meta_path, 'w', encoding='utf-8') as f:
            json.dump(git_info, f, indent=2, default=str)
        print(f"✅ Raw Git metadata saved to: {git_meta_path}")
    except Exception as e:
        print(f"❌ Failed to save raw Git metadata: {e}")

    # 6. Create generation_summary.json (as mentioned in create_readme)
    summary = {
        "generation_date": datetime.datetime.now().isoformat(),
        "status": "Success",
        "repository_path": str(repo_path),
        "output_directory": str(saver.output_dir),
        "files_generated": [
            str(p) for p in [md_path, html_path, meta_path, struct_path, readme_path, git_meta_path] if p
        ]
    }
    summary_path = saver.output_dir / "generation_summary.json"
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"✅ Generation summary saved to: {summary_path}")
    except Exception as e:
        print(f"❌ Failed to save generation summary: {e}")

    return summary

def complete_pipeline_with_git():
    """
    Example of complete pipeline with Git integration
    """
    # Your previous pipeline steps would go here...
    # For demonstration, let's create mock analysis results
    
    analysis_results = {
        'analysis_data': {
            'file_count': 42,
            'file_types': {'Python': 15, 'Markdown': 5, 'Other': 22},
            'structure': {
                'src': ['main.py', 'utils.py'],
                'tests': ['test_main.py'],
                'docs': ['README.md']
            },
            'component_summary': 'Core application with utility modules and tests. (This is mock data)'
        },
        'documentation': 'Auto-generated documentation content...'
    }
    

    repo_path = "/home/blackheart03/codebase_genius_collete/C.O.R.I.A.N" 
    print("="*50)
    print(f"⚠️  WARNING: Using current directory as repo_path: {os.path.abspath(repo_path)}")
    print("⚠️  Please update 'repo_path' in complete_pipeline_with_git() to your target repository if this is incorrect.")
    print("="*50)
    
    # Step 5: Save Results with Git integration
    try:
        save_summary = save_results_pipeline(analysis_results, repo_path, "C.O.R.I.A.N_documentation")
        if save_summary:
            print("🎉 Pipeline completed successfully!")
            print(json.dumps(save_summary, indent=2))
        else:
            print("❌ Pipeline finished with errors.")
        return save_summary
    except Exception as e:
        print(f"❌ Pipeline failed with unhandled exception: {e}")
        traceback.print_exc()
        return None

# ⬇️ THIS LINE RUNS THE PIPELINE ⬇️
if __name__ == "__main__":
    complete_pipeline_with_git()