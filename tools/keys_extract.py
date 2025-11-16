import json
import re
import argparse
from pathlib import Path

TRANSLATABLE_KEYS = {"name", "text", "game_title", "description", "world_name", "memo", "character_name", "message"}
OUTPUT_FILENAME = "_translate_keys.json"

def contains_japanese(text):
    """Check if a string contains Hiragana, Katakana, or CJK characters."""
    if not isinstance(text, str):
        return False
    # This regex covers Hiragana, Katakana, and common CJK Ideographs
    return re.search(r'[\u3040-\u30ff\u4e00-\u9faf]', text)

def find_strings_in_json(data, collected_strings):
    """Recursively traverse a JSON structure to find translatable strings."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key in TRANSLATABLE_KEYS and contains_japanese(value):
                collected_strings.add(value)
            else:
                find_strings_in_json(value, collected_strings)
    elif isinstance(data, list):
        for item in data:
            find_strings_in_json(item, collected_strings)

def should_skip_path(path: Path, root: Path) -> bool:
    """Check if the path should be skipped:
    - If any parent folder starts with '__'
    - If the file starts with '_translate'
    """
    # Check if any part of the relative path starts with '__'
    relative_parts = path.relative_to(root).parts
    if any(part.startswith('__') for part in relative_parts[:-1]):  # exclude filename itself
        return True
    # Check if the file name starts with '_translate'
    if path.name.startswith('_translate'):
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Extracts translatable strings from JSON files in a directory.")
    parser.add_argument("target_directory", type=Path, help="Directory containing the JSON files to process.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Scan for JSON files recursively in subdirectories.")
    args = parser.parse_args()

    if not args.target_directory.is_dir():
        print(f"Error: Directory not found at '{args.target_directory}'")
        return

    output_file_path = args.target_directory / OUTPUT_FILENAME
    all_translations = {}
    total_unique_strings = 0

    print(f"Starting extraction from '{args.target_directory}'...")
    
    glob_pattern = "**/*.json" if args.recursive else "*.json"
    json_files = sorted(list(args.target_directory.glob(glob_pattern)))

    for json_file in json_files:
        if json_file.name == OUTPUT_FILENAME:
            continue
        if should_skip_path(json_file, args.target_directory):
            continue

        unique_strings_for_file = set()
        try:
            content = json.loads(json_file.read_text(encoding="utf-8"))
            find_strings_in_json(content, unique_strings_for_file)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not process {json_file.name}: {e}")
            continue

        if unique_strings_for_file:
            key = str(json_file.relative_to(args.target_directory))
            all_translations[key] = {
                original: "TODO" for original in sorted(list(unique_strings_for_file))
            }
            total_unique_strings += len(unique_strings_for_file)

    if not all_translations:
        print("No translatable strings found.")
        return

    try:
        with output_file_path.open("w", encoding="utf-8") as f:
            json.dump(all_translations, f, indent=4, ensure_ascii=False)
        print(f"Success: Extracted {total_unique_strings} unique strings to '{output_file_path}'.")
    except IOError as e:
        print(f"Error: Could not write to '{output_file_path}': {e}")

if __name__ == "__main__":
    main()