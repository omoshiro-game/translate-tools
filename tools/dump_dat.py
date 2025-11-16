#!/usr/bin/env python3
import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Union

from files import (
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
    return value.lower().replace(".dat", "")


def detect_type(path: Path) -> str:
    key = normalise_key(path.name)
    if key in PARSERS:
        return key
    if ".stg4_" in key or key.endswith(".stg4"):
        return "stage4"
    return None


def load_version(path: Path) -> int:
    with path.open("rb") as handle:
        data = handle.read(4)
        if len(data) != 4:
            raise ValueError("Database file is too small to contain a version header")
        return int.from_bytes(data, "little")


def dump_database(path: Path, db_type: Union[str, None]) -> dict:
    if db_type is None:
        db_type = detect_type(path)
    if db_type is None:
        raise ValueError("Unable to determine database type. Use --type to specify it explicitly.")

    parser_cls = PARSERS.get(db_type)
    if parser_cls is None:
        raise ValueError(f"Unsupported database type: {db_type}")

    parser = parser_cls(path)
    if not parser.parse():
        raise RuntimeError(f"Failed to parse {path}")

    version = load_version(path)
    data_dict = asdict(parser.data)

    if db_type == "stage4":
        return {
            "version": getattr(parser, "version", version),
            "payload": data_dict.get("payload", []),
        }

    if db_type == "system":
        return {
            "magic": getattr(parser, "magic", version),
            "data": data_dict,
        }
    
    return {
        "version": version,
        "data": data_dict,
    }


def main() -> None:
    argument_parser = argparse.ArgumentParser(description="Dump ActionEditor4 database files to JSON")
    argument_parser.add_argument("input", type=Path, help="Path to the .dat file")
    argument_parser.add_argument("--type", dest="db_type", help="Database type override (e.g. anime, bgm)")
    argument_parser.add_argument("--out", dest="output", type=Path, help="Output JSON path")

    args = argument_parser.parse_args()
    try:
        payload = dump_database(args.input, normalise_key(args.db_type) if args.db_type else None)
    except Exception as error:  # pragma: no cover - cli tool
        argument_parser.error(str(error))

    json_payload = json.dumps(payload, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(json_payload, encoding="utf-8")
    else:
        print(json_payload)


if __name__ == "__main__":
    main()
