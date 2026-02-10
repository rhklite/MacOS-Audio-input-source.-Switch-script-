---
name: quick-unit-tests
description: Write minimal unit tests for functions and class methods. Use when the user asks for unit tests, quick tests, testing functions/methods, or test coverage for code.
---

# Quick Unit Tests

## Instructions

When writing unit tests for functions and class methods:

1. **One test file per source file** (or mirror layout: `tests/test_foo.py` for `foo.py`).
2. **Test each public function and method** with at least one test (happy path).
3. **Keep tests short**: assert one behavior per test; avoid long setup when a quick fixture or inline data is enough.
4. **Use the project’s test runner** (e.g. pytest, Jest, unittest); match existing test style in the repo.
5. **Name tests clearly**: `test_<function>_<behavior>` or `test_<Method>_<behavior>`.

## Functions

- **Happy path**: Normal inputs, expected output.
- **Edge case**: Empty input, zero, None, or one obvious boundary if it matters.
- **Skip heavy setup**: Prefer inline args and small fixtures over large harnesses.

## Class methods

- **Instance methods**: Create one instance (or minimal fixture), call method, assert result or side effect.
- **Class/static methods**: Call with class or minimal args; assert return or state.
- **No need to test private helpers** unless they encode critical logic; focus on public API.

## Examples

**Python (pytest):**
```python
# test_utils.py
from myapp.utils import add, Greeter

def test_add_returns_sum():
    assert add(2, 3) == 5

def test_add_handles_zero():
    assert add(0, 0) == 0

def test_Greeter_hello_returns_message():
    g = Greeter("World")
    assert g.hello() == "Hello, World"
```

**JavaScript (Jest):**
```javascript
// utils.test.js
const { add, Greeter } = require('./utils');

test('add returns sum', () => {
  expect(add(2, 3)).toBe(5);
});

test('Greeter.hello returns message', () => {
  const g = new Greeter('World');
  expect(g.hello()).toBe('Hello, World');
});
```

## Scope

- Add tests for the functions/methods in the current file or refactor scope.
- Prefer fast, focused tests; add parametrized or more cases only when the user asks for more coverage.
