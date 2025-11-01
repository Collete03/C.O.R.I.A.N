# --- Import Node/Edge Definitions ---
# This uses the modern import syntax for Jac 0.8.x
from "nodes.jac" import repository, folder, file, node, contains;

# --- Import Python Utilities ---
import:py from utils.git_helper { safe_clone };
import:py from utils.readme_parser { find_readme, summarize_readme };
import:py from utils.llm_helper { enhance_readme_summary, is_llm_available };
import:py from utils.error_handler { handle_clone_error, CloneError };
import:py from utils.file_tree { IGNORE_DIRS, IGNORE_FILES };
import:py from os { listdir, path };
import:py from pathlib { Path };

walker repo_mapper {
    """
    Agent responsible for cloning a repository, mapping its file structure
    into a graph, and summarizing the README.
    """
    has repo_url: str;
    has repo_path: str = "./temp_repo";

    can map_repository with entry -> repository {
        """
        Main entry point for the mapper. Clones, builds graph, returns root node.
        """
        print("\n[Repo Mapper] 1. Cloning repository...");
        
        # --- 1. Clone Repository ---
        try {
            success, result = safe_clone(self.repo_url, self.repo_path);
            if not success {
                raise CloneError(result);
            }
            print(f"  ✓ Cloned to: {self.repo_path}");
        } except Exception as e {
            err_msg = handle_clone_error(self.repo_url, e);
            print(f"  ✗ {err_msg}");
            # We raise the exception to stop the supervisor workflow
            raise CloneError(err_msg);
        }

        # --- 2. Create Root Repository Node ---
        repo_name = self.repo_url.rstrip('/').split('/')[-1].replace('.git', '');
        
        # Spawn the root node of our graph
        root_node = spawn here(
            repository(
                repo_url = self.repo_url,
                name = repo_name,
                local_path = self.repo_path
            )
        );

        # --- 3. Find and Summarize README ---
        print("[Repo Mapper] 2. Summarizing README...");
        readme_file_path = find_readme(self.repo_path);
        
        if readme_file_path {
            print(f"  ✓ Found README: {readme_file_path}");
            summary_data = summarize_readme(readme_file_path);
            
            # Enhance with LLM if available and USE_LLM env var is set
            import:py from os { environ };
            if environ.get("USE_LLM") == "true" and is_llm_available() {
                print("  > Enhancing summary with AI...");
                context = {"languages": ["python", "jac"]}; # Simplified context
                enhanced_summary = enhance_readme_summary(summary_data['summary'], context);
                if enhanced_summary {
                    summary_data['summary'] = enhanced_summary;
                    print("  ✓ AI enhancement complete.");
                } else {
                    print("  ! AI enhancement failed, using basic summary.");
                }
            } else {
                print("  ! LLM not configured or disabled, skipping AI summary enhancement.");
            }
            
            # Store summary data *on the graph node*
            root_node.readme_summary = summary_data;
            
        } else {
            print("  ! No README found.");
            root_node.readme_summary = {
                'title': repo_name,
                'summary': 'No README file found in repository.'
            };
        }

        # --- 4. Map File Structure (Recursively) ---
        print("[Repo Mapper] 3. Building file tree graph...");
        self.map_dir(self.repo_path, root_node);
        print("  ✓ File tree graph built.");
        
        # Return the spawned root node to the supervisor
        return root_node;
    }

    can map_dir(current_path: str, parent_node: node) {
        """
        Recursively walk a directory and spawn folder/file nodes.
        'parent_node' can be a node::repository or node::folder.
        """
        try {
            for item in listdir(current_path) {
                if item in IGNORE_DIRS or item in IGNORE_FILES or item.startswith('.'):
                    continue;

                full_path = path.join(current_path, item);
                
                if path.isdir(full_path) {
                    # Spawn a new folder node and attach it to the parent
                    new_folder_node = spawn parent_node(
                        folder(
                            name = item,
                            path = full_path
                        )
                    );
                    # Connect with a 'contains' edge
                    parent_node -[contains]-> new_folder_node;
                    
                    # Recurse into the new folder
                    self.map_dir(full_path, new_folder_node);
                    
                elif path.isfile(full_path) {
                    # Spawn a file node and attach it to the parent
                    new_file_node = spawn parent_node(
                        file(
                            name = item,
                            path = full_path,
                            extension = Path(item).suffix
                        )
                    );
                    # Connect with a 'contains' edge
                    parent_node -[contains]-> new_file_node;
                }
            } 
            } except Exception as e {
                print(f"  ! Warning: Could not map directory {current_path}. Error: {e}");
            }
        }
    }
}
