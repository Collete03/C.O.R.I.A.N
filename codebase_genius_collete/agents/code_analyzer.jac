# --- Import Node/Edge Definitions ---
from "nodes.jac" import repository, folder, file, code_file,
                        function, class_def, walker_def, node_def,
                        edge_def, calls, inherits, defines, contains, node;

# --- Import Python Utilities ---
import:py from utils.python_parser { parse_file_by_extension, build_code_context_graph };
import:py from pathlib { Path };

walker code_analyzer {
    """
    Agent responsible for analyzing the file graph and building
    the Code Context Graph (CCG) on top of it.
    """
    has parsed_files: list = [];
    has ccg_data: dict = {};

    can analyze_codebase with entry {
        """
        Main entry point for the analyzer.
        Walks the graph, finds files, parses them, and builds the CCG.
        """
        print("\n[Code Analyzer] 1. Finding files to analyze...");
        
        # --- 1. Find all 'file' nodes in the graph ---
        # We start at 'here' (the 'repository' node) and
        # traverse all 'contains' edges recursively (using '++')
        # to find nodes of type 'file'.
        file_nodes = (here ++> node::file).obj;
        
        if not file_nodes {
            print("  ! No files found in graph to analyze.");
            return;
        }

        print(f"  ✓ Found {len(file_nodes)} files in graph.");

        # --- 2. Parse all found files ---
        print("[Code Analyzer] 2. Parsing all files...");
        for f in file_nodes {
            parsed = self.parse_file(f);
            if parsed {
                self.parsed_files.append(parsed);
            }
        }
        print(f"  ✓ Parsed {len(self.parsed_files)} supported files.");

        # --- 3. Build the CCG data (as a dictionary) ---
        print("[Code Analyzer] 3. Building CCG data structure...");
        self.ccg_data = build_code_context_graph(self.parsed_files);
        print("  ✓ CCG data structure built.");

        # --- 4. Spawn CCG Nodes and Edges onto the graph ---
        print("[Code Analyzer] 4. Spawning CCG nodes onto graph...");
        self.spawn_ccg_nodes(here, file_nodes);
        print("  ✓ CCG nodes spawned.");

        print("[Code Analyzer] 5. Spawning CCG relationships onto graph...");
        self.spawn_ccg_relationships(here);
        print("  ✓ CCG relationships spawned.");

        print("\n[Code Analyzer] Analysis complete.");
    }

    can parse_file(file_node: file) -> dict {
        """
        Parses a single file using the Python parser utility.
        If successful, upgrades the 'file' node to a 'code_file' node.
        """
        try {
            parsed = parse_file_by_extension(file_node.path);
            if parsed and not parsed.get('error') {
                # --- Upgrade the node ---
                # 'dot' promotes the 'file' node to a 'code_file'
                # and adds new data to it.
                file_node.dot(
                    code_file(
                        lines = len(Path(file_node.path).read_text(encoding="utf-8").split('\n')),
                        language = "python" if file_node.extension == ".py" else "jac"
                    )
                );
                
                # Store the path on the parsed data for later lookup
                parsed['file_path'] = file_node.path;
                return parsed;
                
            } else if parsed.get('error') {
                print(f"  ! Skipping {file_node.name}: {parsed['error']}");
            }
        } except Exception as e {
            print(f"  ! ERROR parsing {file_node.name}: {e}");
        }
        return null;
    }

    can spawn_ccg_nodes(repo: repository, file_nodes: list) {
        """
        Spawns all functions, classes, etc., as nodes on the graph
        and connects them to the file that defines them.
        """
        # Create a quick lookup map for file nodes
        file_map = {};
        for f in file_nodes {
            file_map[f.path] = f;
        }

        # Spawn function nodes
        for func in self.ccg_data.get('functions', []):
            if func['file_path'] in file_map {
                file_node = file_map[func['file_path']];
                spawn file_node(
                    node::function(
                        name = func['name'],
                        signature = f"{func['name']}({', '.join(func['params'])})",
                        params = func['params'],
                        returns = func['returns'] if func['returns'] else "void",
                        docstring = func['docstring'] if func['docstring'] else "",
                        line_start = func['line'],
                        line_end = func['line'] # Simplified
                    )
                ) -[defines]-> file_node;
            }
        
        # Spawn class nodes
        for cls in self.ccg_data.get('classes', []):
            if cls['file_path'] in file_map {
                file_node = file_map[cls['file_path']];
                class_node = spawn file_node(
                    node::class_def(
                        name = cls['name'],
                        docstring = cls['docstring'] if cls['docstring'] else "",
                        line_start = cls['line'],
                        line_end = cls['line'] # Simplified
                    )
                ) -[defines]-> file_node;
                
                # Spawn method nodes (as functions)
                for method in cls.get('methods', []):
                    spawn class_node(
                        node::function(
                            name = method['name'],
                            signature = f"{method['name']}({', '.join(method['params'])})",
                            params = method['params'],
                            returns = method['returns'] if method['returns'] else "void",
                            docstring = method['docstring'] if method['docstring'] else "",
                            line_start = method['line'],
                            line_end = method['line']
                        )
                    ) -[defines]-> class_node;
            }
            
        # Spawn walker nodes (Jac)
        for w in self.ccg_data.get('walkers', []):
            if w['file_path'] in file_map {
                file_node = file_map[w['file_path']];
                spawn file_node(
                    node::walker_def(
                        name = w['name'],
                        docstring = "",
                        line_start = w['line'],
                        line_end = w['line']
                    )
                ) -[defines]-> file_node;
            }
            
        # Spawn node_def nodes (Jac)
        for n in self.ccg_data.get('nodes', []):
            if n['file_path'] in file_map {
                file_node = file_map[n['file_path']];
                spawn file_node(
                    node::node_def(
                        name = n['name'],
                        docstring = "",
                        line_start = n['line'],
                        line_end = n['line']
                    )
                ) -[defines]-> file_node;
            }

    can spawn_ccg_relationships(repo: repository) {
        """
        Finds all spawned CCG nodes and connects them with edges
        like 'calls' and 'inherits'.
        """
        # Create a lookup for all function and class nodes in the graph
        all_funcs = (repo ++> node::function).obj;
        func_map = {};
        for f in all_funcs {
            func_map[f.name] = f;
        }
        
        all_classes = (repo ++> node::class_def).obj;
        class_map = {};
        for c in all_classes {
            class_map[c.name] = c;
        }

        # Spawn relationship edges
        for rel in self.ccg_data.get('relationships', []):
            from_name = rel['from'];
            to_name = rel['to'];
            
            if rel['type'] == 'calls' {
                if from_name in func_map and to_name in func_map {
                    # Connect function -> function
                    func_map[from_name] -[calls]-> func_map[to_name];
                }
                elif from_name in func_map and to_name in class_map {
                    # Connect function -> class (instantiation)
                    func_map[from_name] -[calls]-> class_map[to_name];
                }
            }
            elif rel['type'] == 'inherits' {
                if from_name in class_map and to_name in class_map {
                    # Connect class -> class
                    class_map[from_name] -[inherits]-> class_map[to_name];
                }
            }
        }
    }
}

