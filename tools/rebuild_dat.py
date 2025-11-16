#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from typing import Union, get_args
from dataclasses import is_dataclass, fields

# Import the same file format classes as the dumper
from files import (
    StageHeader,
    Anime,
    AnimeSet,
    Bgm,
    BmpCharaExc,
    CharaEffect,
    Effect,
    Picture,
    ScrEffect,
    Sound,
    SwordType,
    System,
    Stage,
)

# This dictionary is identical to the one in the dumper script
PARSERS = {
    "anime": Anime,
    "animeset": AnimeSet,
    "bgm": Bgm,
    "bmp_charaexc": BmpCharaExc,
    "charaeffect": CharaEffect,
    "effect": Effect,
    "picture": Picture,
    "screffect": ScrEffect,
    "sound": Sound,
    "swordtype": SwordType,
    "system": System,
    "stage4": Stage,
}


def normalise_key(value: str) -> str:
    """Helper to normalize the db_type key from a filename."""
    if not value:
        return ""
    # For rebuilding, we primarily get the key from the json filename stem
    return value.lower().replace(".json", "")



def _from_dict(data_class, data):
    """
    Recursively creates dataclass instances from a dictionary.
    """
    if not is_dataclass(data_class):
        return data

    field_types = {f.name: f.type for f in fields(data_class)}
    kwargs = {}
    for key, value in data.items():
        if key not in field_types:
            continue
        
        field_type = field_types[key]
        
        # Handle lists of dataclasses
        origin = getattr(field_type, '__origin__', None)
        if origin is list:
            # Get the type of items in the list (e.g., SwordTypeElement from List[SwordTypeElement])
            list_item_type = get_args(field_type)[0]
            kwargs[key] = [_from_dict(list_item_type, item) for item in value]
        # Handle nested single dataclasses
        elif is_dataclass(field_type):
            kwargs[key] = _from_dict(field_type, value)
        # Handle primitive types
        else:
            kwargs[key] = value
            
    return data_class(**kwargs)

def rebuild_database(json_path: Path, output_path: Path, db_type: str) -> None:
    """
    Rebuilds a database file from its JSON representation.
    """
    # 1. Find the appropriate parser class for the given type
    parser_cls = PARSERS.get(db_type)
    if parser_cls is None:
        raise ValueError(f"Unsupported database type: {db_type}")

    # 2. Read and parse the input JSON file
    print(f"Reading JSON from: {json_path}")
    json_content = json_path.read_text(encoding="utf-8")
    payload = json.loads(json_content)

    # 3. Instantiate the parser and populate it with data from the JSON
    # We assume the parser can be instantiated without a file path.
    parser = parser_cls(output_path)
    print(f"Rebuilding with parser: {parser_cls.__name__}")

    # Handle the different JSON structures created by the dumper
    if db_type == "stage4":
        # Stage files have 'version' and 'payload' keys
        parser.version = payload.get("version")
        json_payload_data = payload.get("payload", {})
        
        # Manually reconstruct the complex StageData object
        parser.data.header = _from_dict(StageHeader, json_payload_data.get("header", {}))
        parser.data.palette_payload = json_payload_data.get("palette_payload", [])

    elif db_type == "system":
        # System file has a 'magic' number instead of 'version'
        parser.magic = payload.get("magic")
        parser.data = _from_dict(parser.data.__class__, payload.get("data", {}))
        
    else: # For all other standard files
        parser.version = payload.get("version")
        parser.data = _from_dict(parser.data.__class__, payload.get("data", {}))
        
    build_method_name = None
    # Check for possible method names in order of preference
    for method_name in ['serialize', 'save', 'build']:
        if hasattr(parser, method_name) and callable(getattr(parser, method_name)):
            build_method_name = method_name
            break
            
    if not build_method_name:
        raise NotImplementedError(f"The '{db_type}' parser class does not have a 'serialize', 'save', or 'build' method.")

    print(f"Building binary data using '{build_method_name}' method...")

    build_method = getattr(parser, build_method_name)
    result = build_method()

    if build_method_name == 'save':
        if not result:
             raise RuntimeError(f"The save process for '{db_type}' failed.")
    # 'serialize' and 'build' should return bytes
    else:
        binary_data = result
        if not binary_data:
            raise RuntimeError(f"The build process for '{db_type}' returned no data.")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(binary_data)
        
    print(f"✅ Successfully rebuilt database file at: {output_path}")


def main() -> None:
    argument_parser = argparse.ArgumentParser(description="Rebuild ActionEditor4 database files from JSON")
    argument_parser.add_argument("input", type=Path, help="Path to the input .json file")
    argument_parser.add_argument("--type", dest="db_type", help="Database type (e.g. anime, bgm). Auto-detected if omitted.")
    argument_parser.add_argument("--out", dest="output", type=Path, help="Path for the output file. Auto-generated if omitted.")

    args = argument_parser.parse_args()

    db_type = None
    if args.db_type:
        db_type = normalise_key(args.db_type)
    else:
        # Auto-detect from input filename's stem (e.g., "Anime.json" -> "Anime")
        detected_type = normalise_key(args.input.stem)
        if detected_type in PARSERS:
            db_type = detected_type
            print(f"Auto-detected type: '{db_type}'")
        else:
            argument_parser.error(
                f"Could not auto-detect type from '{args.input.name}'. "
                f"Please specify a valid type with --type."
            )
            
    output_path = args.output
    if not output_path:
        input_stem = args.input.stem # The filename without extension
        
        if db_type == "stage4":
            # For stages, we need the version number for the file extension
            try:
                payload = json.loads(args.input.read_text(encoding="utf-8"))
                version = payload.get("version")
                if version is None:
                    raise ValueError("'version' key not found in stage4 JSON")
                output_filename = f"{input_stem}.stg4_{version}"
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                argument_parser.error(f"Failed to read version from JSON for auto-naming output file: {e}")
        else:
            # For all other types, the output is a .dat file
            output_filename = f"{input_stem}.dat"
            
        # Place the output file in the same directory as the input file
        output_path = args.input.with_name(output_filename)
        print(f"Auto-generated output path: '{output_path}'")

    rebuild_database(args.input, output_path, db_type)


if __name__ == "__main__":
    main()