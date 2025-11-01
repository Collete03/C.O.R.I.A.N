# --- Import Node/Edge Definitions ---
from "nodes.jac" import repository, folder, file, code_file,
                        function, class_def, walker_def, node_def,
                        edge_def, calls, inherits, defines, contains, node;

# --- Import Python Utilities ---
import:py from utils.markdown_generator { 
    function_md, class_md, walker_md, node_md,
    generate_mermaid_class_diagram, generate_mermaid_call_graph 
};
import:py from utils.file_tree { build_file_tree_md };
import:py from pathlib { Path };
import:py from datetime { datetime };
import:py jac; # Import the jac module to access version

walker doc_genie {
    """
    Agent responsible for generating the final Markdown documentation
    by walking the completed graph.
    """
    has doc_content: list = [];
    has repo_node: repository;

    can generate_documentation with entry {
        """
        Main entry point for the document generator.
        """
        print("\n[DocGenie] 1. Starting documentation generation...");
        self.repo_node = here; # 'here' is the 'repository' node

        # --- 1. Create Output Directory ---
        output_dir = f"./outputs/{self.repo_node.name}";
        Path(output_dir).mkdir(parents=True, exist_ok=True);
        self.repo_node.output_path = f"{output_dir}/docs.md";
        print(f"  ✓ Output directory set: {output_dir}");

        # --- 2. Build Documentation Sections ---
        print("[DocGenie] 2. Building sections...");
        self.doc_content = [];
        self.doc_content.append(self.generate_header());
        self.doc_content.append(self.generate_overview());
        self.doc_content.append(self.generate_file_structure());
        self.doc_content.append(self.generate_api_reference());
        self.doc_content.append(self.generate_diagrams());
        self.doc_content.append(self.generate_footer());
        print("  ✓ All sections built.");

        # --- 3. Write Final Markdown File ---
        print(f"[DocGenie] 3. Writing to file: {self.repo_node.output_path}");
        final_doc_str = '\n'.join(self.doc_content);
        try {
            Path(self.repo_node.output_path).write_text(final_doc_str, encoding="utf-8");
            print("  ✓ Documentation saved successfully.");
        } except Exception as e {
            print(f"  ✗ ERROR: Failed to write documentation file: {e}");
            raise Exception(f"Failed to write file: {e}");
        }

        print("\n[DocGenie] Documentation generation complete.");
    }

    # --- Section Generators ---

    can generate_header -> str {
        """Generates the title and repository link."""
        title = self.repo_node.readme_summary.get('title', self.repo_node.name);
        header = f"# {title}\n\n";
        header += f"**Repository:** [{self.repo_node.repo_url}]({self.repo_node.repo_url})\n\n";
        header += "---\n\n";
        return header;
    }

    can generate_overview -> str {
        """Generates the project overview and statistics."""
        section = "## 1. Project Overview\n\n";
        
        # Add README summary
        summary = self.repo_node.readme_summary.get('summary', 'No description available.');
        section += f"{summary}\n\n";

        # Add Installation section if found
        if self.repo_node.readme_summary.get('installation') {
            section += "### Installation\n\n";
            section += "```\n";
            section += self.repo_node.readme_summary['installation'];
            section += "\n```\n\n";
        }

        # --- Gather Graph Statistics ---
        print("  > Gathering graph statistics...");
        all_files = (self.repo_node ++> node::file).obj;
        code_files = (self.repo_node ++> node::code_file).obj;
        funcs = (self.repo_node ++> node::function).obj;
        classes = (self.repo_node ++> node::class_def).obj;
        walkers = (self.repo_node ++> node::walker_def).obj;
        
        total_lines = 0;
        py_count = 0;
        jac_count = 0;
        for cf in code_files {
            total_lines += cf.lines;
            if cf.language == "python" {
                py_count += 1;
            } else if cf.language == "jac" {
                jac_count += 1;
            }
        }

        # --- Add Statistics Table ---
        section += "### Repository Statistics\n\n";
        section += "| Metric | Value |\n";
        section += "| --- | --- |\n";
        section += f"| Total Files Analyzed | {len(all_files)} |\n";
        section += f"| Code Files (Python) | {py_count} |\n";
        section += f"| Code Files (Jac) | {jac_count} |\n";
        section += f"| Total Lines of Code | {total_lines} |\n";
        section += f"| Total Functions Found | {len(funcs)} |\n";
        section += f"| Total Classes Found | {len(classes)} |\n";
        section += f"| Total Walkers Found (Jac) | {len(walkers)} |\n";
        
        section += "\n---\n\n";
        return section;
    }

    can generate_file_structure -> str {
        """Generates the file tree section."""
        print("  > Generating file structure...");
        section = "## 2. File Structure\n\n";
        
        # Call the Python utility to walk the graph and build the tree string
        # We pass self.repo_node (which is a 'repository' node)
        tree_md = build_file_tree_md(self.repo_node);
        
        section += tree_md;
        section += "\n---\n\n";
        return section;
    }

    can generate_api_reference -> str {
        """Generates the API reference for all code elements."""
        print("  > Generating API reference...");
        section = "## 3. API Reference\n\n";

        # Get all code files, sorted by path
        code_files = (self.repo_node ++> node::code_file).obj;
        sorted_files = code_files.sort(key=lambda x: x.path);

        for cf in sorted_files {
            # Add file as a sub-header
            relative_path = cf.path.replace(self.repo_node.local_path + '/', '');
            section += f"### `{relative_path}`\n\n";

            # --- Jac Walkers ---
            # Find walkers defined in this file
            walkers = (cf +<--[defines]- node::walker_def).obj;
            if len(walkers) > 0 {
                section += "#### Walkers\n\n";
                for w in walkers {
                    section += walker_md(w.serialize());
                }
            }
            
            # --- Jac Nodes ---
            nodes = (cf +<--[defines]- node::node_def).obj;
            if len(nodes) > 0 {
                section += "#### Node Definitions\n\n";
                for n in nodes {
                    section += node_md(n.serialize());
                }
            }

            # --- Python/Jac Classes ---
            classes = (cf +<--[defines]- node::class_def).obj;
            if len(classes) > 0 {
                section += "#### Classes\n\n";
                for c in classes {
                    # Get methods defined *by* this class
                    methods = (c +<--[defines]- node::function).obj;
                    # Serialize the node and methods to pass to Python
                    method_dicts = [m.serialize() for m in methods];
                    section += class_md(c.serialize(), method_dicts);
                }
            }

            # --- Python/Jac Functions ---
            # We only want top-level functions, not methods
            all_funcs = (cf +<--[defines]- node::function).obj;
            top_level_funcs = [];
            for f in all_funcs {
                # Check if it has an incoming 'defines' edge from a class
                if len((f +<--[defines]- node::class_def).obj) == 0 {
                    top_level_funcs.append(f);
                }
            }
            
            if len(top_level_funcs) > 0 {
                section += "#### Functions\n\n";
                for f in top_level_funcs {
                    section += function_md(f.serialize());
                }
            }
            
            section += "\n";
        }

        section += "\n---\n\n";
        return section;
    }

    can generate_diagrams -> str {
        """Generates Mermaid diagrams for class hierarchy and function calls."""
        print("  > Generating diagrams...");
        section = "## 4. Codebase Diagrams\n\n";

        # --- Class Diagram ---
        classes = (self.repo_node ++> node::class_def).obj;
        inherits_edges = (self.repo_node ++> node::class_def) -[inherits]-> (self.repo_node ++> node::class_def);
        
        if len(classes) > 0 {
            section += "### Class Hierarchy\n\n";
            # Serialize nodes and edges to pass to Python
            class_dicts = [c.serialize() for c in classes];
            edge_list = [];
            for edge in inherits_edges {
                edge_list.append(
                    {
                        "from_node": edge.parent.obj.serialize(),
                        "to_node": edge.target.obj.serialize()
                    }
                );
            }
            section += generate_mermaid_class_diagram(class_dicts, edge_list);
            section += "\n\n";
        } else {
            section += "### Class Hierarchy\n\nNo classes found.\n\n";
        }

        # --- Call Graph ---
        # Find all 'calls' edges starting from a function
        calls_edges = (self.repo_node ++> node::function) -[calls]-> (self.repo_node);
        
        if len(calls_edges) > 0 {
            section += "### Function Call Graph (Sample)\n\n";
            edge_list = [];
            for edge in calls_edges {
                edge_list.append(
                    {
                        "from_node": edge.parent.obj.serialize(),
                        "to_node": edge.target.obj.serialize()
                    }
                );
            }
            section += generate_mermaid_call_graph(edge_list);
            section += "\n\n";
        } else {
            section += "### Function Call Graph\n\nNo function calls detected.\n\n";
        }

        section += "---\n\n";
        return section;
    }

    can generate_footer -> str {
        """Generates the timestamped footer."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC");
        footer = f"*Documentation generated by Codebase Genius (Jac v{jac.version()}) on {timestamp}*\n";
        return footer;
    }
}
