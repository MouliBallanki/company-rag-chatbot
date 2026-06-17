---
name: sync-docs
description: >-
  Synchronise README.md, plan.md, and any other documentation files whenever
  code changes. Use this skill whenever a service, pipeline, config setting,
  CLI flag, file path, or project structure is added, renamed, or removed.
---

# Sync Docs

Keep documentation in lockstep with the code. Stale docs are worse than no docs.

## When to Trigger

Run this skill automatically after **any** of the following changes:

- A new service, pipeline class, or module is added or removed
- A public method signature changes (name, parameters, return type)
- A `config.py` setting is added, renamed, or its default value changes
- A CLI flag in `ingest.py` or `retrieve.py` is added, renamed, or removed
- A new supported file type is added to `ingestion/parser.py`
- The project folder structure changes (new directory, renamed file)
- `requirements.txt` or `pyproject.toml` dependencies change

## Files to Update

| File | What to check |
|---|---|
| `README.md` | Quick Start commands, project structure tree, configuration table |
| `plan.md` | Architecture diagram, service contracts, pipeline pseudocode, CLI usage |
| `.skills/*/SKILL.md` | References to file paths, method names, or settings that changed |

## Workflow

### Step 1 — Identify what changed
Read the diff of the modified files. List every public interface that changed:
- Method names and signatures
- Config keys and defaults
- CLI argument names
- Directory or file paths

### Step 2 — Update README.md
- **Project Structure** section: reflect any new/renamed/removed files
- **Configuration table**: sync with the actual values in `config.py`
- **CLI Usage** section: sync with the actual argparse definitions in `ingest.py` and `retrieve.py`
- **Quick Start**: verify every command still works end-to-end

### Step 3 — Update plan.md
- **Architecture diagram**: update node labels if service/pipeline names changed
- **Service Contracts**: update method signatures to match the actual code
- **Pipeline pseudocode**: update variable names and method calls
- **CLI Usage**: sync with README.md

### Step 4 — Verify consistency
Cross-check these three facts are identical across all docs:
1. The list of services and their public methods
2. The list of config keys and their defaults
3. The CLI commands and their flags

### Step 5 — Report changes
After updating, summarise what was changed in one short paragraph so the developer can review.

## Rules

- Never invent documentation for code that does not exist yet
- Never remove a section — if a section no longer applies, update its content
- Keep the README Quick Start under 50 lines — it must stay scannable
- Use the exact same names as the code (no paraphrasing method names)
