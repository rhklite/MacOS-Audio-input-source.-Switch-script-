---
name: docstrings-for-methods
description: Add docstrings to all methods. Use when the user asks for docstrings, method documentation, or documenting functions/methods.
---

# Docstrings for All Methods

## Instructions

When adding or refactoring methods:

1. **Add a docstring** to every method/function (no undocumented public methods).
2. **One-line or short**: Prefer one line; use a short paragraph only when needed.
3. **Describe purpose**: What the method does, not how (e.g. "Return the current theme" not "Returns the value of self.theme").
4. **Params/returns**: For non-obvious signatures, include Args/Returns/Raises (or equivalent) in the docstring.

## Pattern

- **Every method**: Each function or method gets a docstring directly under its definition.
- **Style**: Follow the project’s existing docstring style (e.g. Google, NumPy, reST, or plain).
- **No placeholders**: Use real descriptions; avoid "TODO" or "No description" unless temporary.

## Examples

**Python:**
```python
def get_theme():
    """Return the current theme name."""
    return self.theme
```

**With params:**
```python
def set_mode(name, persist=True):
    """Set display mode. If persist is True, save across sessions."""
    ...
```

**JavaScript (JSDoc):**
```javascript
/**
 * Returns the current theme name.
 */
function getTheme() { ... }
```

**Shell (comment above):**
```bash
# Switch to the given audio input device by name.
switch_input() { ... }
```

## Scope

- Apply to all methods in the current file or refactor scope.
- Match existing style in the file; if none, use a consistent style (e.g. Google for Python).
