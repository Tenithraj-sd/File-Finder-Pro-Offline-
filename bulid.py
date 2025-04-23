import os
import json
from pathlib import Path

def build_structure(root_path):
    structure = {
        "type": "directory",
        "name": root_path.name,
        "path": str(root_path),
        "children": []
    }
    
    # Path cache to avoid repeated lookups
    path_cache = {str(root_path): structure}
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip hidden directories
        if any(part.startswith('.') for part in Path(dirpath).parts):
            continue
            
        current_node = path_cache.get(dirpath)
        
        # Process directories first
        for dirname in dirnames.copy():
            if dirname.startswith('.'):
                dirnames.remove(dirname)
                continue
                
            full_path = Path(dirpath) / dirname
            dir_node = {
                "type": "directory",
                "name": dirname,
                "path": str(full_path),
                "children": []
            }
            current_node["children"].append(dir_node)
            path_cache[str(full_path)] = dir_node

        # Process files
        for filename in filenames:
            if filename.startswith('.'):
                continue
                
            full_path = Path(dirpath) / filename
            name, ext = os.path.splitext(filename)
            file_node = {
                "type": "file",
                "name": filename,
                "path": str(full_path),
                "extension": ext[1:] if ext else ""
            }
            current_node["children"].append(file_node)
            
    return structure

def main():
    root_path = Path("/home/tenith/")
    output_file = "file_structure.json"
    
    if not root_path.exists():
        print(f"Error: Path {root_path} does not exist")
        return
        
    print(f"Building structure for {root_path}...")
    structure = build_structure(root_path)
    
    with open(output_file, "w") as f:
        json.dump(structure, f, indent=2)
        
    print(f"Structure saved to {output_file}")

if __name__ == "__main__":
    main()