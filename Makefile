.PHONY: lint lint-fix format format-check typecheck test test-setup coverage protobuf check

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

test-setup:
	docker build -t model_repo_for_lwpython_tests -f tests/docker/Dockerfile tests/docker

test:
	PYTHONPATH=src python -m unittest discover tests

coverage:
	coverage run --rcfile=.coveragerc --source=src -m unittest discover tests
	coverage report -m
	coverage html
	@echo "HTML report: htmlcov/index.html"

protobuf:
	protoc --proto_path=./src --python_out=./src --mypy_out=./src -I . ./src/lionweb/serialization/proto/Chunk.proto

check: format-check lint typecheck test
