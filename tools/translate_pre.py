import json
import argparse
from pathlib import Path

TRANSLATION_FILENAME = "_translate_keys.json"
TODO_FILENAME = "_todo.json"
PRE_TRANSLATION_FILENAME = "_translate_keys_pre.json"
TRANSLATION_DATA_DIR = "_translate"

def find_translation_directory(base_dir):
    """Find translation directory with fallback system."""
    base_path = Path(base_dir)
    
    # List of possible translation directory paths to check
    possible_paths = [
        base_path / TRANSLATION_DATA_DIR,  # data\stg4\_translate
        base_path.parent / TRANSLATION_DATA_DIR,  # data\_translate (if base is data\stg4)
        Path(TRANSLATION_DATA_DIR)  # _translate (relative to current directory)
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path
    
    return None

def load_all_translations(translation_dir):
    """Load all translation files from the translation directory into a flat dict."""
    translation_dir_path = Path(translation_dir)
    if not translation_dir_path.exists():
        print(f"Warning: Translation directory '{translation_dir_path}' not found.")
        return {}
    
    all_translations = {}
    
    for json_file in translation_dir_path.glob("*.json"):
        try:
            content = json.loads(json_file.read_text(encoding="utf-8"))
            # Flatten the nested structure: { "level_name": { "jp": "en" } } -> { "jp": "en" }
            for level_key, translations in content.items():
                if isinstance(translations, dict):
                    for jp_text, en_text in translations.items():
                        if isinstance(jp_text, str) and isinstance(en_text, str):
                            all_translations[jp_text] = en_text
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not process {json_file.name}: {e}")
            continue
    
    return all_translations

def apply_pre_translations(translation_map, available_translations):
    """
    Apply available translations to a single translation map.
    Returns the updated map and a set of missing keys.
    """
    updated_map = {}
    missing_keys = set()
    
    for jp_text, current_value in translation_map.items():
        if jp_text in available_translations:
            # Use the pre-existing translation
            updated_map[jp_text] = available_translations[jp_text]
        else:
            # Keep the current value (likely "TODO") and mark as missing
            updated_map[jp_text] = current_value
            if current_value == "TODO":  # Only add to missing if it was originally TODO
                missing_keys.add(jp_text)
    
    return updated_map, missing_keys

def main():
    parser = argparse.ArgumentParser(description="Pre-processes translation keys by applying available translations.")
    parser.add_argument("target_directory", type=Path, help="Directory containing the JSON files and the keys file.")
    args = parser.parse_args()

    translation_file_path = args.target_directory / TRANSLATION_FILENAME

    if not args.target_directory.is_dir():
        print(f"Error: Directory not found at '{args.target_directory}'")
        return
    if not translation_file_path.is_file():
        print(f"Error: Translation file not found at '{translation_file_path}'")
        return
        
    # Find translation directory with fallback system
    translation_dir = find_translation_directory(args.target_directory)
    if translation_dir is None:
        print(f"Warning: No translation directory found. Checked: '{args.target_directory / TRANSLATION_DATA_DIR}', '{args.target_directory.parent / TRANSLATION_DATA_DIR}', and '{Path(TRANSLATION_DATA_DIR)}'")
        available_translations = {}
    else:
        print(f"Found translation directory: '{translation_dir}'")
        # Load all available translations
        available_translations = load_all_translations(translation_dir)
        print(f"Loaded {len(available_translations)} pre-existing translations.")
    
    # Load the original translation keys file
    try:
        all_translations = json.loads(translation_file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error: Could not read or parse '{translation_file_path}': {e}")
        return

    # Process each file's translation map
    updated_translations = {}
    all_missing_keys = set()
    
    for rel_path, translation_map in all_translations.items():
        updated_map, missing_keys = apply_pre_translations(translation_map, available_translations)
        updated_translations[rel_path] = updated_map
        all_missing_keys.update(missing_keys)
    
    # Save the pre-processed translation keys file
    pre_translation_file_path = args.target_directory / PRE_TRANSLATION_FILENAME
    try:
        with pre_translation_file_path.open("w", encoding="utf-8") as f:
            json.dump(updated_translations, f, indent=4, ensure_ascii=False)
        print(f"Saved pre-processed translations to '{pre_translation_file_path}'")
    except IOError as e:
        print(f"Error: Could not write to '{pre_translation_file_path}': {e}")
        return
    
    # Save missing keys as a flat dict for manual translation
    todo_file_path = args.target_directory / TODO_FILENAME
    todo_dict = {key: "TODO" for key in sorted(all_missing_keys)}
    
    try:
        with todo_file_path.open("w", encoding="utf-8") as f:
            json.dump(todo_dict, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(all_missing_keys)} missing translations to '{todo_file_path}'")
    except IOError as e:
        print(f"Error: Could not write to '{todo_file_path}': {e}")
        return

    print("Pre-processing complete.")

if __name__ == "__main__":
    main()