#!/usr/bin/env python3
"""Generate MkDocs pages from table definition folders."""

import html
import json
import re
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML

# Set up logging
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up YAML parser with ruamel.yaml
yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(
    mapping=2, sequence=4, offset=2
)  # Preserve indentation for better readability

# Define paths
SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent.parent
DEFS_DIR = ROOT / "table-definitions"
DOCS_DIR = ROOT / "docs"
TABLES_DIR = DOCS_DIR / "tables"
MKDOCS_YML = ROOT / "mkdocs.yml"
INDEX_MD = DOCS_DIR / "index.md"
DATA_INDEX = DOCS_DIR / "data-tables.md"
DEF_INDEX = DOCS_DIR / "definition-tables.md"

# Setup Jinja2 environment for template rendering
TEMPLATES_DIR = SCRIPT_DIR / "templates"
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR), trim_blocks=True, lstrip_blocks=True
)


def _is_definition_table(table: dict) -> bool:
    """Determine if a table is a definition table."""
    return table.get("type") == "definition"


def _read_definitions_file(
    file_path: Path, headers: list[str] | None = None
) -> str | None:
    """Read a .dat file and return it as a filterable HTML table."""
    if not file_path.exists():
        return "## Values\n\n*No values loaded. Add a .dat file to populate this section.*\n"

    text = file_path.read_text(encoding="utf-8")
    rows = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if "\t" in line:
            parts = line.split("\t")
        else:
            parts = re.split(r"\s{2,}", line)

        rows.append([p.strip() for p in parts])

    if not rows:
        return "## Values\n\n*No values loaded. Add a .dat file to populate this section.*\n"

    # Determine column count from widest row
    col_count = max(len(row) for row in rows)

    # Pad short rows
    for row in rows:
        while len(row) < col_count:
            row.append("")

    # Generate default headers if not provided
    if not headers:
        if col_count == 1:
            headers = ["Value"]
        elif col_count == 2:
            headers = ["Code", "Description"]
        else:
            headers = ["Index"] + [f"Value{i}" for i in range(1, col_count)]

    out = '## Values\n\n<div class="filterable values-table">\n<table>\n<thead>\n<tr>'
    for h in headers:
        out += f"<th>{html.escape(h)}</th>"
    out += "</tr>\n</thead>\n<tbody>\n"
    for row in rows:
        out += "<tr>"
        for cell in row:
            out += f"<td>{html.escape(cell)}</td>"
        out += "</tr>\n"
    out += "</tbody>\n</table>\n</div>\n"

    return out


def generate_table_page(
    table: dict, table_dir: Path, documented_tables: set[str]
) -> str:
    """Generate a Markdown page for a given table definition."""
    table_name = table["name"]

    schema_table = _build_schema_table(table, documented_tables)
    definitions_section = _build_definitions_section(table, table_dir) or ""
    references_section = _build_references_section(table, documented_tables)
    queries_section = _build_queries_section(table, table_dir)

    return env.get_template("table_page.md.j2").render(
        tags=table.get("tags", []),
        table_name=table_name,
        description=table.get("description", ""),
        is_definition=_is_definition_table(table),
        schema_table=schema_table,
        definitions_section=definitions_section,
        references_section=references_section,
        queries_section=queries_section,
    )


def generate_index(data_count: int, def_count: int) -> str:
    """Generate the main index page with counts of data and definition tables."""
    return env.get_template("index.md.j2").render(
        data_count=data_count, def_count=def_count
    )


def generate_type_index(tables: list[dict], title: str, description: str) -> str:
    """Generate an index page for a specific type of table (data or definition)."""
    cards = _build_cards(tables)
    return env.get_template("type_index.md.j2").render(
        title=title, description=description, cards=cards
    )


def _build_schema_table(table: dict, documented_tables: set[str]) -> str:
    """Build the schema table for a given table definition."""
    has_definitions = any(
        col.get("definition_table", "").strip() for col in table["columns"]
    )

    # Schema table header
    if has_definitions:
        header = (
            "| Column | Type | Description | Definition |\n| --- | --- | --- | --- |"
        )
    else:
        header = "| Column | Type | Description |\n| --- | --- | --- |"

    col_rows = []
    for col in table["columns"]:
        desc = col.get("description", "")
        if has_definitions:
            def_table = col.get("definition_table", "").strip()
            if def_table:
                if def_table in documented_tables:
                    def_link = f"[{def_table}]({def_table}.md)"
                else:
                    def_link = def_table
            else:
                def_link = ""
            col_rows.append(
                f"| {col['name']} | `{col['type']}` | {desc} | {def_link} |"
            )
        else:
            col_rows.append(f"| {col['name']} | `{col['type']}` | {desc} |")

    schema_table = (
        '<div class="schema-table" markdown>\n\n'
        + header
        + "\n"
        + "\n".join(col_rows)
        + "\n\n</div>"
    )

    return schema_table


def _build_definitions_section(table: dict, table_dir: Path) -> str | None:
    """Build the definitions section for a given table definition."""
    if not _is_definition_table(table):
        return None

    dat_path = table_dir / f"{table['name']}.dat"
    headers = table.get("definition_headers")
    return _read_definitions_file(dat_path, headers)


def _build_references_section(table: dict, documented_tables: set[str]) -> str:
    """Build the references section for a given table definition."""
    references = table.get("references", [])
    if not references:
        return ""

    references_section = "## Referenced By\n\n"
    for ref in references:
        if ref in documented_tables:
            references_section += f"[{ref}]({ref}.md), "

    return references_section


def _build_queries_section(table: dict, table_dir: Path) -> str:
    """Build the queries section for a given table definition."""
    queries = table.get("queries", [])
    if not queries:
        return "\n*No queries documented yet.*\n"

    queries_section = ""
    for q in queries:
        queries_section += f"\n### {q['name']}\n\n"
        queries_section += f"{q.get('description', '')}\n\n"
        queries_section += f'```sql title="{q["file"]}"\n'
        queries_section += f'--8<-- "table-definitions/{"definition" if _is_definition_table(table) else "data"}/{table["name"]}/sql/{q["file"]}"\n'
        queries_section += "```\n"

    return queries_section


def _build_cards(table_list: list[dict]) -> str:
    """Build a list of cards for the index pages."""
    cards = []
    for t in table_list:
        tags = " ".join(f"`{tag}`" for tag in t["tags"]) if t["tags"] else "*untagged*"

        name = t["name"]
        description = t.get("description", "")
        card = env.get_template("card.md.j2").render(
            name=name, description=description, tags=tags
        )
        cards.append(card)
    return "\n\n".join(cards)


def update_nav():
    """Update the 'nav' section of mkdocs.yml to include the generated pages."""
    with MKDOCS_YML.open("r", encoding="utf-8") as f:
        config = yaml.load(f)

    if not config or "nav" not in config:
        logger.error("mkdocs.yml is missing or does not contain a 'nav' section.")
        return

    config["nav"] = [
        {"Home": "index.md"},
        {"Data Tables": "data-tables.md"},
        {"Definition Tables": "definition-tables.md"},
        {"Tags": "tags.md"},
    ]

    with MKDOCS_YML.open("w", encoding="utf-8") as f:
        yaml.dump(config, f)


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # Each subfolder in table-definitions/data-tables and table-definitions/definition-tables is a table
    table_dirs = sorted(
        table_dir
        for type_dir in DEFS_DIR.iterdir()
        if type_dir.is_dir()
        for table_dir in type_dir.iterdir()
        if table_dir.is_dir()
    )

    if not table_dirs:
        logger.error("No table folders found in %s", DEFS_DIR)
        return

    # First pass - load all tables
    tables = []
    dir_map = {}
    for table_dir in table_dirs:
        json_files = list(table_dir.glob("*.json"))
        if not json_files:
            logger.warning("No JSON file in %s/, skipping", table_dir.name)
            continue

        table = json.loads(json_files[0].read_text())
        tables.append(table)
        dir_map[table["name"]] = table_dir

    # Set of documented table names for link validation
    documented_tables = {t["name"] for t in tables}

    # Second pass - generate pages with validated links
    for table in tables:
        table_dir = dir_map[table["name"]]
        out_path = TABLES_DIR / f"{table['name']}.md"
        out_path.write_text(generate_table_page(table, table_dir, documented_tables))
        logger.info("  Generated %s", out_path.relative_to(ROOT))

    # Split by type
    data_tables, def_tables = [], []
    for table in tables:
        if _is_definition_table(table):
            def_tables.append(table)
        else:
            data_tables.append(table)

    # Generate data and definition index pages
    INDEX_MD.write_text(generate_index(len(data_tables), len(def_tables)))
    logger.info("  Updated %s", INDEX_MD.relative_to(ROOT))

    DATA_INDEX.write_text(
        generate_type_index(
            data_tables, "Data Tables", "Application and business data tables."
        )
    )
    logger.info("  Updated %s", DATA_INDEX.relative_to(ROOT))

    # Generate tags.md for the tags plugin
    TAGS_MD = DOCS_DIR / "tags.md"
    TAGS_MD.write_text(env.get_template("tags.md.j2").render())
    logger.info("  Updated %s", TAGS_MD.relative_to(ROOT))

    # Generate definition tables index
    DEF_INDEX.write_text(
        generate_type_index(
            def_tables,
            "Definition Tables",
            "Validation and lookup tables that define valid codes used across the system.",
        )
    )
    logger.info("  Updated %s", DEF_INDEX.relative_to(ROOT))

    # Update the nav section of mkdocs.yml
    update_nav()
    logger.info("  Updated %s", MKDOCS_YML.relative_to(ROOT))

    print()
    logger.info(
        f"Generated {len(tables)} table page(s) ({len(data_tables)} data, {len(def_tables)} definition)"
    )


if __name__ == "__main__":
    main()
