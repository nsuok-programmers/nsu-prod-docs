# Contributing

Don't push directly to `main`. Create a branch, make your changes, and open a pull request. Then request a review. The site deploys automatically once the PR is merged into `main`.

### Table of Contents

- [Adding a Table](#adding-a-table)
- [Update a Table](#update-a-table)
- [Update a Tool](#update-a-tool)
- [Add a Tool](#add-a-tool)

---

### Adding a Table

#### 0.5. Create a branch

Before starting, create a new branch for your changes:

```bash
git checkout -b add/<tablename>
```

#### 1. Get the .info file

In the SQL editor, run:

```sql
INFO <TABLE_NAME>;
```

Copy the entire output and save it as `<TABLE_NAME>.info` in `tools/info-converter/info-files/`.

#### 2. Convert to JSON

```bash
python tools/info-converter/convert.py           # all files
python tools/info-converter/convert.py SPRIDEN    # single table
```

#### 3. Create the table folder

Move the JSON from `converted/` into a new folder in `table-definitions/`:

```
table-definitions/SPRIDEN/
└── SPRIDEN.json
```

#### 4. Edit the JSON

Fill in `tags`, `definition_table` links on columns, and `queries`. Also change any descriptions that may not be as accurate as we need.

#### 5. Add queries (optional)

Create a `sql/` subfolder and add `.sql` files:

```
table-definitions/SPRIDEN/
├── SPRIDEN.json
└── sql/
    └── find-name.sql
```

Reference them in the JSON:

```json
"queries": [
  {
    "file": "find-name.sql",
    "name": "Find Name by ID",
    "description": "Look up a person's name by their PIDM."
  }
]
```

#### 6. Add lookup values (definition tables only)

Set `"type": "definition"` in the JSON and add a `.dat` file with the raw data:

```
table-definitions/STVDEGC/
├── STVDEGC.json
└── STVDEGC.dat
```

#### 7. Generate and preview
Run either through the CLI tool or REPL

```bash
# Repl
python main.py
#   - Select option 4 (all)
#   - Select option 6 (serve)

# CLI tool
python main.py all
python main.py serve
```

#### 8. Squash and submit PR

If you have multiple commits, squash them into a single commit before opening a PR:

```bash
git rebase -i main
# mark all commits except the first as "squash" or "s"
git push --force-with-lease origin add/<tablename>
```

**Allowed files in an add-table PR:**

- `tools/info-converter/info-files/<TABLENAME>.info`
- `table-definitions/<TABLENAME>/<TABLENAME>.json`
- `table-definitions/<TABLENAME>/<TABLENAME>.dat` (definition tables only)
- `table-definitions/<TABLENAME>/sql/*.sql`

PRs containing other files will be rejected.

- - -

### Update a Table

#### 1. Create a branch

Before starting, create a new branch for your changes:

```bash
git checkout -b update/<tablename>
```

#### 2. Make your changes

Edit the relevant files in `table-definitions/<TABLENAME>/`:

- `<TABLENAME>.json` — update descriptions, tags, column info, or query references
- `<TABLENAME>.dat` — update lookup values (definition tables only)
- `sql/*.sql` — add, modify, or remove query files

#### 3. Generate and preview
Run either through the CLI tool or REPL

```bash
# Repl
python main.py
#   - Select option 4 (all)
#   - Select option 6 (serve)

# CLI tool
python main.py all
python main.py serve
```

#### 4. Squash and submit PR

If you have multiple commits, squash them into a single commit before opening a PR:

```bash
git rebase -i main
# mark all commits except the first as "squash" or "s"
git push --force-with-lease origin update/<tablename>
```

**Allowed files in an update-table PR:**

- `table-definitions/<TABLENAME>/<TABLENAME>.json`
- `table-definitions/<TABLENAME>/<TABLENAME>.dat` (definition tables only)
- `table-definitions/<TABLENAME>/sql/*.sql`

PRs containing other files will be rejected.

- - -

### Update a Tool

#### 1. Create a branch

Before starting, create a new branch for your changes:

```bash
git checkout -b tool/update/<description>
```

#### 2. Make your changes

Edit the relevant tool file:

- `tools/info-converter/convert.py` — converts `.info` files to JSON
- `tools/page-generator/generate.py` — builds markdown from JSON

#### 3. Test your changes

Run the tool and verify the output:

```bash
# For converter changes
python main.py convert

# For generator changes
python main.py generate
python main.py serve
```

#### 4. Squash and submit PR

If you have multiple commits, squash them into a single commit before opening a PR:

```bash
git rebase -i main
# mark all commits except the first as "squash" or "s"
git push --force-with-lease origin tool/update/<description>
```

**Allowed files in an update-tool PR:**

- `tools/info-converter/convert.py`
- `tools/page-generator/generate.py`

PRs containing other files will be rejected.

- - -

### Add a Tool

#### 1. Create a branch

Before starting, create a new branch for your changes:

```bash
git checkout -b tool/add/<description>
```

#### 2. Create your tool

Add a new tool in the `tools/` directory with an appropriate folder structure.

> [!IMPORTANT]
> Do not change `main.py`. Any tools created will be added to `main.py` by primary contributors.

#### 3. Test your changes

Run the tool and verify the output works as expected.

#### 4. Squash and submit PR

If you have multiple commits, squash them into a single commit before opening a PR:

```bash
git rebase -i main
# mark all commits except the first as "squash" or "s"
git push --force-with-lease origin tool/add/<description>
```

**Allowed files in an add-tool PR:**

- `tools/<toolname>/*`

PRs containing files in any other place than the created folder will be rejected.
