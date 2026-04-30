# batch_import_stg4.py
import sys
from pathlib import Path

# Add the 'tools' directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = SCRIPT_DIR / "tools"
sys.path.insert(0, str(TOOLS_DIR))

try:
    from stg4_tool import import_from_json
except ImportError as e:
    print(f"[X] Failed to import stg4_tool: {e}")
    sys.exit(1)

def main():
    # Arguments: source_folder [output_folder]
    if len(sys.argv) < 2:
        print("Usage: python batch_import_stg4.py <source_json_folder> [output_folder]")
        print("Example: python batch_import_stg4.py data/stg4 new/data/stg4")
        sys.exit(1)
    
    source_dir = Path(sys.argv[1])
    output_base = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("new/data/stg4")
    
    if not source_dir.is_dir():
        print(f"[X] Error: '{source_dir}' is not a valid directory.")
        sys.exit(1)
    
    # Create output directory
    output_base.mkdir(parents=True, exist_ok=True)
    
    # Find all JSON files (both .json and .stg4_1020.json)
    json_files = sorted([f for f in source_dir.glob("*.json") if f.is_file()])
    
    if not json_files:
        print("/!\ No .json files found.")
        return
    
    total = len(json_files)
    print(f"Found {total} JSON file(s) to import.")
    print(f"Output folder: {output_base.resolve()}")
    print()
    
    success_count = 0
    fail_count = 0
    
    for i, json_file in enumerate(json_files, 1):
        # Generate output filename: remove .json extension
        # e.g., "MyStage.stg4_1020.json" -> "MyStage.stg4_1020"
        # e.g., "MyStage.json" -> "MyStage.stg4_1020"
        if json_file.name.endswith('.stg4_1020.json'):
            output_name = json_file.name[:-5]  # Remove .json
        else:
            output_name = json_file.name[:-5] + '.stg4_1020'  # Remove .json, add .stg4_1020
        
        output_file = output_base / output_name
        
        print(f"[{i:03d}/{total}] Importing: {json_file.name}")
        print(f"           => {output_file.name}")
        
        try:
            import_from_json(json_file, output_file)
            print(f"           OK Success\n")
            success_count += 1
        except Exception as e:
            print(f"           [X] FAILED: {e}\n")
            fail_count += 1
    
    print("=" * 50)
    print(f"Batch import completed.")
    print(f"   Success: {success_count}")
    print(f"   Failed: {fail_count}")
    print(f"   Output: {output_base.resolve()}")

if __name__ == "__main__":
    main()