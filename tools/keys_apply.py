import json
import argparse
from pathlib import Path

TRANSLATION_FILENAME = "_translate_keys.json"

def apply_translations_to_json(data, translation_map, count):
    """
    Recursively traverse a JSON structure and replace strings
    based on the translation map. Returns the modified data.
    """
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            # Check if this value is a string that needs translation
            if isinstance(value, str) and value in translation_map:
                translated_value = translation_map[value]
                # Only apply if it's not the placeholder
                if translated_value != "TODO":
                    new_dict[key] = translated_value
                    count['replaced'] += 1
                else:
                    new_dict[key] = value
            else:
                new_dict[key] = apply_translations_to_json(value, translation_map, count)
        return new_dict
    elif isinstance(data, list):
        return [apply_translations_to_json(item, translation_map, count) for item in data]
    else:
        return data

def main():
    parser = argparse.ArgumentParser(description="Applies translated strings from a keys file to JSON files.")
    parser.add_argument("target_directory", type=Path, help="Directory containing the JSON files and the keys file.")
    args = parser.parse_args()

    translation_file_path = args.target_directory / TRANSLATION_FILENAME

    if not args.target_directory.is_dir():
        print(f"Error: Directory not found at '{args.target_directory}'")
        return
    if not translation_file_path.is_file():
        print(f"Error: Translation file not found at '{translation_file_path}'")
        return
        
    try:
        all_translations = json.loads(translation_file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error: Could not read or parse '{translation_file_path}': {e}")
        return

    print(f"Applying translations to '{args.target_directory}'...")

    for rel_path, translation_map in all_translations.items():
        json_file_path = args.target_directory / rel_path
        
        if not json_file_path.is_file():
            print(f"Warning: Skipping '{rel_path}', file not found.")
            continue
            
        try:
            original_content = json.loads(json_file_path.read_text(encoding="utf-8"))
            replacement_counter = {'replaced': 0}
            
            modified_content = apply_translations_to_json(original_content, translation_map, replacement_counter)
            
            count = replacement_counter['replaced']
            if count > 0:
                print(f"Patching {rel_path}: {count} strings replaced.")
                with json_file_path.open("w", encoding="utf-8") as f:
                    json.dump(modified_content, f, indent=4, ensure_ascii=False)
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error processing {rel_path}: {e}")

    print("Done.")

if __name__ == "__main__":
    main()