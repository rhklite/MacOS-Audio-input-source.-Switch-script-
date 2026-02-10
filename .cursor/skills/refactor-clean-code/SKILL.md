---
name: refactor-clean-code
description: Refactor messy code into clean, readable shape. Use when the user asks to refactor, clean up code, improve structure, or fix messy or hard-to-read code.
---

# Refactor Messy Code into Clean Shape

## Instructions

When refactoring messy code:

1. **Preserve behavior**: No change in inputs/outputs or side effects; only structure and clarity.
2. **Extract and name**: Long blocks → well-named functions/methods; magic values → named constants.
3. **Reduce nesting**: Early returns, guard clauses, or small functions instead of deep if/else/loop stacks.
4. **Single responsibility**: One clear purpose per function/class; split when one does too much.
5. **Match project style**: Naming, formatting, and patterns already used in the file or repo.
6. **Leave tests green**: If tests exist, run them after refactor; fix any breakage.

## Clean-Shape Checklist

- [ ] No long functions (split at logical boundaries).
- [ ] No magic numbers or strings (use named constants).
- [ ] No deep nesting (flatten with early returns or helpers).
- [ ] Clear names (variables, functions, types).
- [ ] No dead or commented-out code (remove it).
- [ ] Consistent formatting and style.

## Patterns

**Before (messy):**
```python
def process(d):
    if d:
        if d.get("x"):
            if d["x"] > 0:
                v = d["x"] * 2
                if v > 100:
                    return "big"
                else:
                    return "small"
    return None
```

**After (clean):**
```python
def process(data):
    if not data or "x" not in data:
        return None
    value = data["x"] * 2
    return "big" if value > 100 else "small"
```

**Extract helpers:**
- Repeated logic → shared function.
- Complex condition → named function or variable (e.g. `is_valid_order()`).
- Long argument list → object or options dict with clear keys.

## Scope

- Refactor the file or selection the user specified.
- Prefer small, incremental steps; avoid changing unrelated code.
- If the codebase has a style guide or linter, follow it.
