.PHONY: lint format format-check typecheck test check

lint:
	ruff check src/ tests/

lint-fix:
	ruff check --fix src/ tests/

format:
	ruff format src/ tests/

format-check:
	ruff format --check src/ tests/

typecheck:
	mypy src/

test:
	PYTHONPATH=src python -m unittest discover tests

check: format-check lint typecheck test
