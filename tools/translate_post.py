import json
import argparse
from pathlib import Path

PRE_TRANSLATION_FILENAME = "_translate_keys_pre.json"
TODO_FILENAME = "_todo.json"
TRANSLATION_FILENAME = "_translate_keys.json"

def merge_translations(pre_translations, todo_translations):
    """
    Merge pre-processed translations with completed TODO translations.
    Updates any "TODO" values in pre_translations with values from todo_translations.
    """
    merged_translations = {}
    
    for rel_path, translation_map in pre_translations.items():
        merged_map = {}
        for jp_text, current_value in translation_map.items():
            if current_value == "TODO" and jp_text in todo_translations:
                # Use the completed translation
                merged_map[jp_text] = todo_translations[jp_text]
            else:
                # Keep the current value (either pre-translated or original)
                merged_map[jp_text] = current_value
        merged_translations[rel_path] = merged_map
    
    return merged_translations

def main():
    parser = argparse.ArgumentParser(description="Post-processes translation keys by merging completed translations.")
    parser.add_argument("target_directory", type=Path, help="Directory containing the JSON files and the keys file.")
    args = parser.parse_args()

    pre_translation_file_path = args.target_directory / PRE_TRANSLATION_FILENAME
    todo_file_path = args.target_directory / TODO_FILENAME

    if not args.target_directory.is_dir():
        print(f"Error: Directory not found at '{args.target_directory}'")
        return
    if not pre_translation_file_path.is_file():
        print(f"Error: Pre-translation file not found at '{pre_translation_file_path}'")
        return
    if not todo_file_path.is_file():
        print(f"Error: TODO file not found at '{todo_file_path}'")
        return
        
    # Load pre-processed translations
    try:
        pre_translations = json.loads(pre_translation_file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error: Could not read or parse '{pre_translation_file_path}': {e}")
        return
    
    # Load completed TODO translations
    try:
        todo_translations = json.loads(todo_file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error: Could not read or parse '{todo_file_path}': {e}")
        return

    # Merge the translations
    final_translations = merge_translations(pre_translations, todo_translations)
    
    # Save the final merged translation keys file
    final_translation_file_path = args.target_directory / TRANSLATION_FILENAME
    try:
        with final_translation_file_path.open("w", encoding="utf-8") as f:
            json.dump(final_translations, f, indent=4, ensure_ascii=False)
        print(f"Saved final merged translations to '{final_translation_file_path}'")
    except IOError as e:
        print(f"Error: Could not write to '{final_translation_file_path}': {e}")
        return

    print("Post-processing complete.")

if __name__ == "__main__":
    main()