import json
import argparse
from pathlib import Path
from collections import defaultdict

TRANSLATION_FILENAME = "_translate_keys.json"
TODO_FILENAME = "_translatorpp_todo.json"
PRE_TRANSLATION_FILENAME = "_translate_keys_pre.json"
TRANSLATION_DATA_DIR = "_translate"


def find_translation_directory(base_dir):
    """Find translation directory with fallback system."""
    base_path = Path(base_dir)
    
    possible_paths = [
        base_path / TRANSLATION_DATA_DIR,
        base_path.parent / TRANSLATION_DATA_DIR,
        Path(TRANSLATION_DATA_DIR)
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path
    return None


def load_all_translations(translation_dir):
    """Load all translation files into a flat {jp: en} dict."""
    translation_dir_path = Path(translation_dir)
    if not translation_dir_path.exists():
        print(f"Warning: Translation directory '{translation_dir_path}' not found.")
        return {}
    
    all_translations = {}
    
    for json_file in translation_dir_path.glob("*.json"):
        try:
            content = json.loads(json_file.read_text(encoding="utf-8"))
            for level_key, translations in content.items():
                if isinstance(translations, dict):
                    for jp_text, en_text in translations.items():
                        if isinstance(jp_text, str) and isinstance(en_text, str):
                            all_translations[jp_text] = en_text
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not process {json_file.name}: {e}")
            continue
    
    return all_translations


def apply_pre_translations_with_context(translation_map, available_translations, file_name):
    """
    Process a file's translation map and return list of entries with context.
    Returns: list of dicts, and set of missing jp keys.
    """
    entries = []
    missing_keys = set()
    counter = 1  # per-file index starting at 1

    for jp_text, current_value in translation_map.items():
        context = f"{file_name}/{counter}"
        counter += 1

        # Determine translation: prefer available, fallback to current ("TODO" or existing)
        translation = available_translations.get(jp_text, current_value)

        entries.append({
            "text": jp_text,
            "translation": "",  # <-- always empty
            "context": context
        })

        missing_keys.add(jp_text)  # All keys are effectively "missing" since translation is blank

    return entries, missing_keys


def main():
    parser = argparse.ArgumentParser(description="Pre-processes translation keys into structured array format.")
    parser.add_argument("target_directory", type=Path, help="Directory containing the JSON files and the keys file.")
    args = parser.parse_args()

    translation_file_path = args.target_directory / TRANSLATION_FILENAME

    if not args.target_directory.is_dir():
        print(f"[!] Error: Directory not found at '{args.target_directory}'")
        return
    if not translation_file_path.is_file():
        print(f"[!] Error: Translation file not found at '{translation_file_path}'")
        return
        
    # Find translation directory
    translation_dir = find_translation_directory(args.target_directory)
    if translation_dir is None:
        print(f"Warning: No translation directory found. Using empty pre-translation set.")
        available_translations = {}
    else:
        print(f"Found translation directory: '{translation_dir}'")
        available_translations = load_all_translations(translation_dir)
        print(f"Loaded {len(available_translations)} pre-existing translations.")
    
    # Load original translation keys
    try:
        all_translations = json.loads(translation_file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        print(f"[!] Error: Could not read or parse '{translation_file_path}': {e}")
        return

    # Process each file's map into structured entries
    all_entries = []  # Final list of all entries (to dump as array)
    all_missing_keys = set()

    for file_name, translation_map in all_translations.items():
        if not isinstance(translation_map, dict):
            print(f"/!\\ Warning: Skipping non-dict entry for file '{file_name}'")
            continue
        entries, missing_keys = apply_pre_translations_with_context(translation_map, available_translations, file_name)
        all_entries.extend(entries)
        all_missing_keys.update(missing_keys)

    # Save pre-processed structured list
    pre_translation_file_path = args.target_directory / PRE_TRANSLATION_FILENAME
    try:
        with pre_translation_file_path.open("w", encoding="utf-8") as f:
            json.dump(all_entries, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(all_entries)} structured entries to '{pre_translation_file_path}'")
    except IOError as e:
        print(f"[!] Error: Could not write to '{pre_translation_file_path}': {e}")
        return

    todo_file_path = args.target_directory / TODO_FILENAME
    try:
        with todo_file_path.open("w", encoding="utf-8") as f:
            json.dump(all_entries, f, indent=4, ensure_ascii=False)
        print(f"Saved {len(all_entries)} missing entries to '{todo_file_path}'")
    except IOError as e:
        print(f"[!] Error: Could not write to '{todo_file_path}': {e}")
        return

    print("Pre-processing complete.")


if __name__ == "__main__":
    main()