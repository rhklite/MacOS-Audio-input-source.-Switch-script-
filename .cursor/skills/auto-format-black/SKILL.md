---
name: auto-format-black
description: Auto-format Python files using Black. Use when the user asks to format with Black, auto-format Python, or run Black on files.
---

# Auto-Format Files Using Black

## Instructions

When the user asks to format files with Black:

1. **Run Black** on the target file(s) or directory.
2. **Default command**: `black <path>` (format in place).
3. **Check only** if the user asks to check without changing: `black --check <path>`.
4. **Respect config**: Use project `pyproject.toml`, `setup.cfg`, or `.black` if present; otherwise use Black defaults (line length 88, etc.).
5. **Target**: Format the file(s) the user specified, or current file; for "all", use the project root or `src`/package dir as appropriate.

## Commands

**Format file(s) in place:**
```bash
black path/to/file.py
black path/to/dir/
```

**Check only (no write):**
```bash
black --check path/to/file.py
```

**With config (project root):**
```bash
black .
```

## Scope

- Run Black on the path the user gave, or the current file.
- If the project has a Black config, do not override it with CLI flags unless the user asks.
- Install hint if Black is missing: `pip install black` or `uv add --dev black`.
