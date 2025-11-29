# PyCardGolf

A Python implementation of a card golf game.

## Development Setup

### Installing Dependencies

```bash
poetry install
```

### Pre-commit Hooks

This project uses `pre-commit` hooks to ensure code quality. The hooks include:
- **Black**: Code formatting
- **Trailing whitespace removal**
- **End of file fixer**
- **YAML validation**

To install the pre-commit hooks:

```bash
poetry run pre-commit install
```

The hooks will now run automatically on every commit. To run them manually:

```bash
poetry run pre-commit run --all-files
```

### Running Tests

```bash
poetry run pytest
```

Run tests with coverage:

```bash
poetry run pytest --cov=pycardgolf --cov-report=term-missing
```

Run only unit tests:

```bash
poetry run pytest tests/unit
```

Run only integration tests:

```bash
poetry run pytest -m integration
```
