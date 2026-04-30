# batch_export_stg4.py
import sys
from pathlib import Path

# Add the 'tools' directory to sys.path so we can import stg4_tool directly
SCRIPT_DIR = Path(__file__).resolve().parent
TOOLS_DIR = SCRIPT_DIR / "tools"
sys.path.insert(0, str(TOOLS_DIR))

try:
    from stg4_tool import export_to_json
except ImportError as e:
    print(f"[X] Failed to import stg4_tool: {e}")
    print("   Ensure 'tools/stg4_tool.py' exists in the same directory as this script.")
    sys.exit(1)

def main():
    # Accept target folder as CLI argument, fallback to your example path
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "data/stg4"
    target_path = Path(target_dir)

    if not target_path.is_dir():
        print(f"[X] Error: '{target_dir}' is not a valid directory.")
        sys.exit(1)

    # Collect all matching files
    files = sorted(target_path.glob("*.stg4_1020"))
    if not files:
        print("/!\ No .stg4_1020 files found.")
        return

    total = len(files)
    print(f"<i> Found {total} file(s) to export. Starting...\n")

    for i, file_path in enumerate(files, 1):
        # Progress reporting (newline-based to avoid messing up if export_to_json prints)
        print(f"[{i:03d}/{total}] Exporting: {file_path.name}")
        try:
            # Direct function call: bypasses argparse & subprocess
            export_to_json([file_path])
            print(f"      [OK] Success\n")
        except Exception as e:
            print(f"      [X] FAILED: {e}\n")

    print("Batch export completed.")

if __name__ == "__main__":
    main()