import json
import argparse
from pathlib import Path
from collections import defaultdict

PRE_TRANSLATION_FILENAME = "_translate_keys_pre.json"
TODO_FILENAME = "_translatorpp_todo.json"
TRANSLATION_FILENAME = "_translate_keys.json"
TRANSLATION_DATA_DIR = "_translate"



def load_structured_translations(filepath):
    """Load structured array and return dict: {(filename, text): translation}"""
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        raise RuntimeError(f"Failed to load {filepath.name}: {e}")

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array in {filepath.name}")

    lookup = {}
    for entry in data:
        text = entry.get("text")
        translation = entry.get("translation", "")
        context = entry.get("context", "")

        if not isinstance(text, str) or not isinstance(context, str):
            continue  # skip invalid

        if '/' not in context:
            continue

        filename = context.split('/', 1)[0]  # everything before first '/'

        # Only store non-empty translations
        if translation and translation.strip():
            lookup[(filename, text)] = translation.strip()

    return lookup

def main():
    parser = argparse.ArgumentParser(
        description="Post-process: merge structured translations back into original _translate_keys.json format."
    )
    parser.add_argument("target_directory", type=Path, help="Directory containing the JSON files.")
    args = parser.parse_args()

    dir_path = args.target_directory
    pre_path = dir_path / PRE_TRANSLATION_FILENAME
    todo_path = dir_path / TODO_FILENAME
    orig_keys_path = dir_path / TRANSLATION_FILENAME  # input skeleton

    # All files must exist
    for path, name in [
        (orig_keys_path, "Original translation keys (_translate_keys.json)"),
        (pre_path, "Pre-translation file"),
        (todo_path, "TODO file")
    ]:
        if not path.is_file():
            print(f"[!] Error: {name} not found at '{path}'")
            return

    # Load original structure (the template we’ll update)
    try:
        original = json.loads(orig_keys_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError) as e:
        print(f"[!] Error loading {TRANSLATION_FILENAME}: {e}")
        return

    if not isinstance(original, dict):
        print("[!] Error: _translate_keys.json must be a JSON object.")
        return

    # Load structured translations — priority: TODO > PRE (so load PRE first, then override with TODO)
    try:
        pre_lookup = load_structured_translations(pre_path)
        todo_lookup = load_structured_translations(todo_path)
    except (RuntimeError, ValueError) as e:
        print(f"[!] {e}")
        return

    # Merge: TODO overrides PRE
    merged_lookup = {**pre_lookup, **todo_lookup}

    # Now update original in-place
    updated_count = 0
    removed_count = 0
    missing_report = []  # list of (filename, jp_text)

    # Update & clean original map
    for filename, text_map in list(original.items()):  # list() in case we delete files
        if not isinstance(text_map, dict):
            continue

        new_text_map = {}
        for jp_text, current_val in text_map.items():
            key = (filename, jp_text)

            # Priority 1: use merged translation if available
            if key in merged_lookup:
                new_text_map[jp_text] = merged_lookup[key]
                updated_count += 1
            # Priority 2: keep value only if it's NOT "TODO" (case-insensitive)
            elif isinstance(current_val, str) and current_val.strip().upper() != "TODO":
                new_text_map[jp_text] = current_val
            else:
                # It's "TODO" (or empty/"todo") → remove & report
                removed_count += 1
                missing_report.append((filename, jp_text))

        # Replace map (even if empty)
        original[filename] = new_text_map

        # Optional: remove files that became empty
        if not new_text_map:
            del original[filename]
            print(f"(i) File '{filename}' is now empty and was removed.")

    # Save updated translation file
    try:
        with orig_keys_path.open("w", encoding="utf-8") as f:
            json.dump(original, f, indent=4, ensure_ascii=False)
        print(f"Updated {updated_count} translations, removed {removed_count} 'TODO' entries.")
        print(f"   Final: {len(original)} files, {sum(len(v) for v in original.values())} keys.")
    except IOError as e:
        print(f"[!] Failed to write output: {e}")
        return

    # Report missing
    if missing_report:
        print(f"\n/!\\ {len(missing_report)} untranslated entries were removed (were 'TODO'):")
        for filename, jp in missing_report[:10]:  # show first 10
            print(f"   • '{jp}' in '{filename}'")
        if len(missing_report) > 10:
            print(f"   ... and {len(missing_report) - 10} more.")
    else:
        print("All entries were translated !")

    print("Post-processing complete.")


if __name__ == "__main__":
    main()