#!/usr/bin/env python3
"""
Parse .info files into JSON for MkDocs generation.

Reads .info files in the "info-files" subdirectory, extracts table metadata and columns,
and writes structured JSON files to the "converted" subdirectory.

Usage:
  python convert.py                # Convert all .info files
  python convert.py SPRIDEN        # Convert only SPRIDEN.info (Case-insensitive)
"""

import json
import re
import sys
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent
INPUT_DIR = SCRIPT_DIR / "info-files"
OUTPUT_DIR = SCRIPT_DIR / "converted"


def parse_info(filepath: str) -> dict:
    text = Path(filepath).read_text()
    lines = text.splitlines()

    result = {
        "name": "",
        "description": "",
        "type": "data",
        "tags": [],
        "queries": [],
        "columns": [],
    }

    # Extract table name
    for line in lines:
        match = re.match(r"TABLE:\s*(\S+)", line)
        if match:
            result["name"] = match.group(1)
            break

    # Extract table comment
    for line in lines:
        match = re.match(r"\s*COMMENTS\s*:(.*)", line)
        if match:
            result["description"] = match.group(1).strip()
            break

    # Find the columns section
    col_start = None
    for i, line in enumerate(lines):
        if re.match(r"\s*NAME\s+DATA TYPE\s+NULL", line):
            col_start = i + 1
            break

    if col_start is None:
        return result

    # Find where columns end (blank line or next section like "Indexes")
    col_end = len(lines)
    for i in range(col_start, len(lines)):
        stripped = lines[i].strip()
        if (
            stripped == ""
            or stripped.startswith("Indexes")
            or stripped.startswith("INDEX_NAME")
        ):
            col_end = i
            break

    # Parse columns - new column starts with space + uppercase name
    # Continuation lines are heavily indented with no column name pattern
    col_pattern = re.compile(
        r"^[\s*]([A-Z][A-Z0-9_]+)\s+"  # column name (leading space or * for primary key)
        r"([\w()., ]+?)\s{2,}"  # data type (stop at 2+ spaces)
        r"(Yes|No)\s*"  # nullable (no longer requires trailing space)
        r"(.*)"  # rest is default + comment (can be empty)
    )

    columns = []
    current = None

    for i in range(col_start, col_end):
        line = lines[i]
        match = col_pattern.match(line)

        if match:
            if current:
                columns.append(current)

            name = match.group(1).strip()
            dtype = match.group(2).strip()
            remainder = match.group(4).strip()

            current = {
                "name": name,
                "type": dtype,
                "description": remainder,
                "definition_table": "",
            }
        elif current and line.strip():
            current["description"] += " " + line.strip()

    if current:
        columns.append(current)

    # Clean up multi-space artifacts from column-aligned formatting
    for col in columns:
        col["description"] = re.sub(r"\s{2,}", " ", col["description"]).strip()

    result["columns"] = columns
    return result


def main():
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1:
        # Convert a single table
        table_name = sys.argv[1].upper()
        target = INPUT_DIR / f"{table_name}.info"
        if not target.exists():
            logger.error(f"File not found: {target}")
            return
        files = [target]
    else:
        # Convert all
        files = sorted(INPUT_DIR.glob("*.info"))

    if not files:
        logger.info(f"No .info files found in {INPUT_DIR}")
        return

    for f in files:
        result = parse_info(str(f))
        out_path = OUTPUT_DIR / f"{result['name']}.json"
        out_path.write_text(json.dumps(result, indent=2) + "\n")
        logger.info(f"{f.name} -> {out_path.name}  ({len(result['columns'])} columns)")

    print()
    logger.info(f"Converted {len(files)} file(s) to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
