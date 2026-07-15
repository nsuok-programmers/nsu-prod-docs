"""
Main CLI entry point for NSU-Prod-Docs tools. This script provides a command-line interface for various tools:
    - info-converter: Converts .info files to JSON format.
    - page-generator: Generates markdown pages from JSON files.
    - reference-updater: Updates references in JSON files based on .info files.

Usage:
    python main.py                  # Launch interactive REPL
    python main.py convert [TABLE]  # Convert .info files to JSON (all, or one table)
    python main.py update-refs      # Update table references
    python main.py generate         # Generate MkDocs pages
    python main.py all [TABLE]      # Run convert, update-refs, and generate in sequence (all, or one table)

    # MKDocs commands:
    python main.py status           # Show pipeline gaps (unconverted/unplaced tables)
    python main.py build            # Build the MkDocs site (--strict)
    python main.py serve            # Serve the MkDocs site locally
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent
CONVERT_SCRIPT = ROOT / "tools" / "info-converter" / "convert.py"
UPDATE_REFS_SCRIPT = ROOT / "tools" / "reference-updater" / "update-references.py"
GENERATE_SCRIPT = ROOT / "tools" / "page-generator" / "generate.py"

INFO_DIR = ROOT / "tools" / "info-converter" / "info-files"
CONVERTED_DIR = ROOT / "tools" / "info-converter" / "converted"
DEFS_DIR = ROOT / "table-definitions"


def _run(cmd: list[str]) -> bool:
    """Run a command as a subprocess, streaming its output. Return True on success."""
    result = subprocess.run(cmd)
    return result.returncode == 0


def run_script(script: Path, args: list[str] | None = None) -> bool:
    """Run a tool script as a subprocess, streaming its output. Return True on success."""
    return _run([sys.executable, str(script), *(args or [])])


def run_convert(table: str | None = None) -> bool:
    return run_script(CONVERT_SCRIPT, [table] if table else None)


def run_update_refs() -> bool:
    return run_script(UPDATE_REFS_SCRIPT)


def run_generate() -> bool:
    return run_script(GENERATE_SCRIPT)


def run_all(table: str | None = None) -> bool:
    return run_convert(table) and run_update_refs() and run_generate()


def run_build() -> bool:
    return _run([sys.executable, "-m", "mkdocs", "build", "--strict"])


def run_serve() -> bool:
    return _run([sys.executable, "-m", "mkdocs", "serve"])


def run_status() -> bool:
    """Report where each table sits in the pipeline: raw .info, converted JSON, or placed."""
    info_tables = {f.stem.upper() for f in INFO_DIR.glob("*.info")}
    converted_tables = {f.stem.upper() for f in CONVERTED_DIR.glob("*.json")}

    placed_tables = {}
    if DEFS_DIR.exists():
        for type_dir in DEFS_DIR.iterdir():
            if not type_dir.is_dir():
                continue
            for table_dir in type_dir.iterdir():
                if table_dir.is_dir():
                    placed_tables[table_dir.name.upper()] = table_dir

    unconverted = sorted(info_tables - converted_tables - placed_tables.keys())
    unplaced = sorted(converted_tables - placed_tables.keys())

    logger.info("Info files awaiting conversion: %d", len(unconverted))
    for name in unconverted:
        logger.info("    %s", name)

    logger.info(
        "Converted JSON awaiting move into table-definitions/: %d", len(unplaced)
    )
    for name in unplaced:
        logger.info("    %s  (tools/info-converter/converted/%s.json)", name, name)

    logger.info("Tables placed in table-definitions/: %d", len(placed_tables))

    return True


def _prompt_table() -> str | None:
    value = input("Table name (blank for all): ").strip()
    return value or None


def repl():
    """Interactive menu that routes to the same stage functions used by the CLI."""
    options = {
        "1": ("Convert .info files to JSON", lambda: run_convert(_prompt_table())),
        "2": ("Update table references", run_update_refs),
        "3": ("Generate MkDocs pages", run_generate),
        "4": ("Run all stages", lambda: run_all(_prompt_table())),
        "5": ("Show pipeline status", run_status),
        "6": ("Build MkDocs site (--strict)", run_build),
        "7": ("Serve MkDocs site locally", run_serve),
    }

    while True:
        print("\nNSU-Prod-Docs Tools")
        for key, (label, _) in options.items():
            print(f"  {key}) {label}")
        print("  q) Quit")

        choice = input("\nSelect an option: ").strip().lower()

        if choice in ("q", "quit", "exit"):
            break
        if choice not in options:
            print("Invalid option.")
            continue

        label, action = options[choice]
        print(f"\n--- {label} ---\n")
        if not action():
            logger.error("Stage failed.")


def main():
    parser = argparse.ArgumentParser(
        description="CLI for NSU-Prod-Docs tools: convert .info files, update references, and generate MkDocs pages."
    )
    subparsers = parser.add_subparsers(dest="command")

    p_convert = subparsers.add_parser("convert", help="Convert .info files to JSON")
    p_convert.add_argument(
        "table", nargs="?", help="Convert a single table (case-insensitive)"
    )

    subparsers.add_parser(
        "update-refs", help="Update table references from .info files"
    )
    subparsers.add_parser(
        "generate", help="Generate MkDocs pages from table-definitions"
    )

    p_all = subparsers.add_parser(
        "all", help="Run convert, update-refs, and generate in sequence"
    )
    p_all.add_argument(
        "table", nargs="?", help="Convert only this table before running the rest"
    )

    subparsers.add_parser(
        "status", help="Show pipeline gaps (unconverted/unplaced tables)"
    )
    subparsers.add_parser("build", help="Build the MkDocs site (--strict)")
    subparsers.add_parser("serve", help="Serve the MkDocs site locally")

    args = parser.parse_args()

    if args.command is None:
        repl()
        return

    if args.command == "convert":
        success = run_convert(args.table)
    elif args.command == "update-refs":
        success = run_update_refs()
    elif args.command == "generate":
        success = run_generate()
    elif args.command == "all":
        success = run_all(args.table)
    elif args.command == "status":
        success = run_status()
    elif args.command == "build":
        success = run_build()
    elif args.command == "serve":
        success = run_serve()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
