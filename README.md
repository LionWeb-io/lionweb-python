# LionWeb Python

[![PyPI version](https://img.shields.io/pypi/v/lionweb)](https://pypi.org/project/lionweb-python/)

This library contains an implementation in Python of the LionWeb specifications.

This library is released under the Apache V2 License.

Read the [Documentation](https://lionweb.io/lionweb-python)

We support Python 3.11 to 3.14

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

Releases are published to PyPI from a local machine with `release.sh`.

1. Install the release tools: `pip install bump2version build twine`, and configure
   your PyPI credentials in `~/.pypirc`.
2. On `main`, move the entries of the upcoming version into their section in
   `CHANGELOG.md`, commit and push.
3. Run `./release.sh` (or `./release.sh minor` / `./release.sh major`).

The script checks that you are on a clean `main` in sync with `origin/main`, then:

* bumps the version in `src/lionweb/__init__.py` (the only place it is written;
  `pyproject.toml` reads it from there) and in `.bumpversion.cfg`, committing the
  change and creating the `vX.Y.Z` tag
* builds the sdist and wheel into `dist/`
* pushes `main` and the tag
* uploads the package to PyPI
