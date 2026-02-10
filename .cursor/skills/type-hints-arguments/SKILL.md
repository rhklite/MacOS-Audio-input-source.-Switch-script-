---
name: type-hints-arguments
description: Add type hints to every function and method argument. Use when the user asks for type hints, typing arguments, or annotating parameters.
---

# Type Hints on Every Argument

## Instructions

When adding type hints to arguments:

1. **Annotate every parameter** of every function and method (no untyped args).
2. **Annotate return type** when non-obvious or when the project already uses return hints.
3. **Use the language’s standard typing** (e.g. `typing` in Python, TypeScript/JSDoc in JS).
4. **Match project style**: Optional vs `| None`, `list[X]` vs `List[X]`, etc.
5. **Keep it accurate**: Use the real types the code expects; avoid `Any` unless necessary.

## Pattern

- **Every argument**: Each parameter gets a type hint.
- **Returns**: Add return type for public functions/methods when the project uses them.
- **Generics**: Use type vars or generic types when the function is generic (e.g. `T`, `list[T]`).

## Examples

**Python:**
```python
def greet(name: str, count: int = 1) -> str:
    return (name + " ") * count

def process(items: list[str], options: dict[str, bool] | None = None) -> int:
    ...
```

**TypeScript:**
```typescript
function greet(name: string, count: number = 1): string {
  return (name + " ").repeat(count);
}
```

**JSDoc (JavaScript):**
```javascript
/**
 * @param {string} name
 * @param {number} [count=1]
 * @returns {string}
 */
function greet(name, count = 1) { ... }
```

## Scope

- Apply to the current file or selection.
- Follow existing typing style in the file (e.g. `Optional[X]` vs `X | None`).
- Use `Any` only when the type is truly unknown; prefer `object` or a union when possible.
