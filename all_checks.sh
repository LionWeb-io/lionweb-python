ruff check src/ tests/ && mypy src/ && PYTHONPATH=src python -m unittest discover tests && black src/ tests/ && isort src/ tests/
