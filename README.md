# LionWeb Python

[![PyPI version](https://img.shields.io/pypi/v/lionweb)](https://pypi.org/project/lionweb-python/)

This library contains an implementation in Python of the LionWeb specifications.

This library is released under the Apache V2 License.

Read the [Documentation](https://lionweb.io/lionweb-python)

We support Python 3.11 to 3.13

## Development

Install the package and its dependencies in editable mode:

```
pip install -e ".[dev]" ruff mypy mypy-protobuf types-requests
```

## Common tasks

All common tasks are available via `make`:

| Command | Description |
|---|---|
| `make check` | Run all checks (format, lint, typecheck, tests) |
| `make test-setup` | Build the Docker image required for integration tests (run once) |
| `make test` | Run the test suite |
| `make coverage` | Run tests with coverage and generate an HTML report under `htmlcov/` |
| `make format` | Auto-format code with Ruff |
| `make format-check` | Check formatting without modifying files |
| `make lint` | Lint with Ruff |
| `make lint-fix` | Lint and auto-fix fixable issues |
| `make typecheck` | Type-check with MyPy |
| `make protobuf` | Regenerate Protobuf classes from `Chunk.proto` |

## Build locally

```
pip install build
python -m build
```

## Release process

* Update version in `pyproject.toml` and `src/lionweb/__init__.py`
* Create tag: `git tag -a v0.1.1 -m "Version 0.1.1"`
* Release on PyPI:

```
pip install setuptools wheel twine
python setup.py sdist bdist_wheel
twine upload dist/*
```
* Push tag
