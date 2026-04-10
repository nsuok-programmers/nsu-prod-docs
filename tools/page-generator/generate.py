#!/usr/bin/env python3
"""Generate MkDocs pages from table definition folders."""

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent.parent
DEFS_DIR = ROOT / "table-definitions"
DOCS_DIR = ROOT / "docs"
TABLES_DIR = DOCS_DIR / "tables"
MKDOCS_YML = ROOT / "mkdocs.yml"
INDEX_MD = DOCS_DIR / "index.md"
DATA_INDEX = DOCS_DIR / "data-tables.md"
DEF_INDEX = DOCS_DIR / "definition-tables.md"


def read_definitions_file(file_path: Path, headers: list[str] | None = None) -> str | None:
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

    html = '## Values\n\n'

    # Input
    html += '<input type="text" id="values-filter" placeholder="Filter values..." '
    html += 'style="margin-bottom:1rem;padding:0.5rem;width:25%;border:1px solid var(--md-default-fg-color--lighter);border-radius:0.25rem;background:var(--md-default-bg-color);color:var(--md-default-fg-color);" '
    html += 'onkeyup="(function(e){var q=e.value.toLowerCase();document.querySelectorAll(\'#values-table tbody tr\').forEach(function(r){r.style.display=r.textContent.toLowerCase().includes(q)?\'\':\'none\'})})(this)">\n\n'

    # Table
    html += '<table id="values-table" style="display:inline-block;height:400px;overflow-y:auto;table-layout:fixed;">\n'
    html += '<thead style="position:sticky;top:0;background:var(--md-default-bg-color);z-index:1;">\n<tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr>\n</thead>\n<tbody>\n'
    for row in rows:
        html += '<tr>'
        for cell in row:
            html += f'<td>{cell}</td>'
        html += '</tr>\n'
    html += '</tbody>\n</table>\n'

    return html


def generate_table_page(table: dict, table_dir: Path, documented_tables: set[str]) -> str:
    tags_yaml = "\n".join(f"  - {t}" for t in table["tags"])
    table_type = table.get("type", "data")
    table_name = table["name"]

    # Check if any column has a non-empty definition table link
    has_definitions = any(
        col.get("definition_table", "").strip()
        for col in table["columns"]
    )

    # Schema table
    if has_definitions:
        header = "| Column | Type | Description | Definition |\n| --- | --- | --- | --- |"
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
            col_rows.append(f"| {col['name']} | `{col['type']}` | {desc} | {def_link} |")
        else:
            col_rows.append(f"| {col['name']} | `{col['type']}` | {desc} |")

    schema_table = '<div class="schema-table" markdown>\n\n' + header + "\n" + "\n".join(col_rows) + '\n\n</div>'

    # Type badge
    if table_type == "definition":
        type_badge = "!!! abstract \"Definition Table\"\n    This is a validation/lookup table that defines valid codes for other tables.\n"
    else:
        type_badge = ""

    # Definitions section - auto-detect .dat file
    definitions_section = ""
    if table_type == "definition":
        dat_path = table_dir / f"{table_name}.dat"
        headers = table.get("definition_headers")
        definitions_section = read_definitions_file(dat_path, headers)

    # References section
    references_section = ""
    refs = table.get("references", [])
    if refs:
        references_section = "## Referenced By\n\n"
        for ref in refs:
            if ref in documented_tables:
                references_section += f"[{ref}]({ref}.md), "

    # Queries section
    queries_section = ""
    for q in table.get("queries", []):
        print(q["file"])
        queries_section += f"\n### {q['name']}\n\n"
        queries_section += f"{q.get('description', '')}\n\n"
        queries_section += f'```sql title="{q["file"]}"\n'
        queries_section += f'--8<-- "table-definitions/{"definition" if table.get("type") == "definition" else "data"}/{table_name}/sql/{q["file"]}"\n'
        queries_section += "```\n"

    if not table.get("queries"):
        queries_section = "\n*No queries documented yet.*\n"

    md = f"""---
tags:
{tags_yaml}
---

# {table_name}

{table['description']}

{type_badge}
## Schema

{schema_table}

{definitions_section}
{references_section}
## Queries
- - -
{queries_section}"""

    return md


def build_cards(table_list: list[dict]) -> str:
    cards = []
    for t in table_list:
        tags = " ".join(f"`{tag}`" for tag in t["tags"]) if t["tags"] else "*untagged*"
        cards.append(f"""-   **{t['name']}**

    ---

    {t['description']}

    **Tags:** {tags}

    [:octicons-arrow-right-24: View table](tables/{t['name']}.md)""")
    return "\n\n".join(cards)


def generate_index(data_count: int, def_count: int) -> str:
    return f"""---
hide:
  - navigation
  - toc
---

# Banner Table Dictionary

Search for tables, schemas, and queries using the search bar above, or browse by category.

---

<div class="grid cards" markdown>

-   :material-database:{{ .lg .middle }} **Data Tables**

    ---

    {data_count} tables containing application and business data.

    [:octicons-arrow-right-24: Browse data tables](data-tables.md)

-   :material-book-open-variant:{{ .lg .middle }} **Definition Tables**

    ---

    {def_count} validation and lookup tables that define valid codes.

    [:octicons-arrow-right-24: Browse definition tables](definition-tables.md)

</div>
"""


def generate_type_index(tables: list[dict], title: str, description: str) -> str:
    return f"""---
hide:
  - navigation
  - toc
---

# {title}

{description}

---

<div class="grid cards" markdown>

{build_cards(tables)}

</div>
"""


def update_nav():
    """Rewrite nav to static structure - individual tables accessed via search and cards."""
    text = MKDOCS_YML.read_text()

    new_nav = """nav:
  - Home: index.md
  - Data Tables: data-tables.md
  - Definition Tables: definition-tables.md
  - Tags: tags.md
"""

    text = re.sub(
        r"nav:\n(  - .*\n)+",
        new_nav,
        text
    )

    MKDOCS_YML.write_text(text)


def main():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # Each subfolder in table-definitions/data-tables and table-definitions/definition-tables is a table
    table_dirs = sorted(
        table_dir
        for type_dir in DEFS_DIR.iterdir() if type_dir.is_dir()
        for table_dir in type_dir.iterdir() if table_dir.is_dir()
    )

    if not table_dirs:
        print(f"No table folders found in {DEFS_DIR}")
        return

    # First pass - load all tables
    tables = []
    dir_map = {}
    for table_dir in table_dirs:
        json_files = list(table_dir.glob("*.json"))
        if not json_files:
            print(f"  WARNING: No JSON file in {table_dir.name}/, skipping")
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
        print(f"  Generated {out_path.relative_to(ROOT)}")

    # Split by type
    data_tables = [t for t in tables if t.get("type", "data") == "data"]
    def_tables = [t for t in tables if t.get("type") == "definition"]

    # Generate index pages
    INDEX_MD.write_text(generate_index(len(data_tables), len(def_tables)))
    print(f"  Updated {INDEX_MD.relative_to(ROOT)}")

    DATA_INDEX.write_text(generate_type_index(
        data_tables,
        "Data Tables",
        "Application and business data tables."
    ))
    print(f"  Updated {DATA_INDEX.relative_to(ROOT)}")

    # Generate tags.md for the tags plugin
    TAGS_MD = DOCS_DIR / "tags.md"
    TAGS_MD.write_text("""---
hide:
  - navigation
  - toc
---

# Tags

<!-- This page is auto-populated by the tags plugin -->

[TAGS]
""")
    print(f"  Updated {TAGS_MD.relative_to(ROOT)}")
    DEF_INDEX.write_text(generate_type_index(
        def_tables,
        "Definition Tables",
        "Validation and lookup tables that define valid codes used across the system."
    ))
    print(f"  Updated {DEF_INDEX.relative_to(ROOT)}")

    update_nav()
    print(f"  Updated {MKDOCS_YML.relative_to(ROOT)}")

    print(f"\nGenerated {len(tables)} table page(s) ({len(data_tables)} data, {len(def_tables)} definition)")


if __name__ == "__main__":
    main()
