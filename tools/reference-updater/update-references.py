#!/usr/bin/env python3
"""
Update references for all table definitions by scanning .info files.

Parses the References section from each .info file, filters against tables
that exist in table-definitions/, and updates each JSON file's references
field in place.

Usage:
  python update-references.py
"""

import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent.parent
INFO_DIR = ROOT / "tools" / "info-converter" / "info-files"
DEFS_DIR = ROOT / "table-definitions"


def get_documented_tables() -> set[str]:
    """Get set of table names that have folders in table-definitions/."""
    return {d.name.upper() for d in DEFS_DIR.iterdir() if d.is_dir()}


def parse_references_from_info(filepath: Path) -> list[str]:
    """Parse the References section from an .info file and return all referenced table names."""
    text = filepath.read_text()
    lines = text.splitlines()

    ref_start = None
    for i, line in enumerate(lines):
        if line.strip().startswith("References"):
            ref_start = i + 1
            break

    if ref_start is None:
        return []

    # Skip the header row
    for i in range(ref_start, len(lines)):
        if lines[i].strip().startswith("TABLE_NAME"):
            ref_start = i + 1
            break

    referenced_tables = set()
    for i in range(ref_start, len(lines)):
        line = lines[i].strip()
        if not line:
            break

        parts = line.split()
        if parts:
            referenced_tables.add(parts[0].upper())

    return sorted(referenced_tables)


def build_reference_map() -> dict[str, list[str]]:
    """Build a map of table_name -> [tables that reference it] from all .info files."""
    ref_map = {}

    for info_file in sorted(INFO_DIR.glob("*.info")):
        table_name = info_file.stem.upper()
        refs = parse_references_from_info(info_file)
        ref_map[table_name] = refs

    return ref_map


def update_json_references(ref_map: dict[str, list[str]], documented_tables: set[str]):
    """Update the references field in each table-definitions JSON file."""
    updated = 0

    for table_dir in sorted(DEFS_DIR.iterdir()):
        if not table_dir.is_dir():
            continue

        json_files = list(table_dir.glob("*.json"))
        if not json_files:
            continue

        json_path = json_files[0]
        table = json.loads(json_path.read_text())
        table_name = table["name"].upper()

        # Get references for this table, filtered to only documented tables
        all_refs = ref_map.get(table_name, [])
        filtered_refs = [r for r in all_refs if r in documented_tables]

        # Update only if changed
        old_refs = table.get("references", [])
        if filtered_refs != old_refs:
            table["references"] = filtered_refs
            json_path.write_text(json.dumps(table, indent=2) + "\n")
            logger.info("  Updated %s (%d references)", table_name, len(filtered_refs))
            updated += 1
        else:
            logger.info(
                "  No change %s (%d references)", table_name, len(filtered_refs)
            )

    return updated


def main():
    if not INFO_DIR.exists():
        logger.error(f"Info files directory not found: {INFO_DIR}")
        return

    if not DEFS_DIR.exists():
        logger.error(f"Table definitions directory not found: {DEFS_DIR}")
        return

    logger.info("Building reference map from .info files...")
    ref_map = build_reference_map()
    logger.info(f"  Parsed {len(ref_map)} .info files\n")

    logger.info("Updating table definitions...")
    documented_tables = get_documented_tables()
    updated = update_json_references(ref_map, documented_tables)
    print()
    logger.info(f"  {updated} table(s) updated")


if __name__ == "__main__":
    main()
