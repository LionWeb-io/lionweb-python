---
sidebar_position: 10
---

# Contributing to LionWeb Python

Thank you for your interest in contributing to LionWeb Python! This document provides guidelines and instructions for contributing to the project.


## Getting Started

1. Fork the repository
2. Clone your fork
3. Ensure Python and Docker are installed (Docker is needed for running tests)
4. Set up the development environment:
   ```
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   
   # Necessary before being able to run tests
   sh prepare_for_tests.sh
   ```
4. Create a new branch for your changes

## Development Workflow

1. **Create an Issue**: Before starting work, create an issue describing the problem or feature
2. **Branch Naming**: Use descriptive branch names (e.g., `fix/issue-123` or `feature/new-feature`)
3. **Code Style**: Follow the project's code style guidelines
   ```
   # Run these before committing
   black src/ tests/
   isort src/ tests/
   ruff check src/ tests/
   mypy src/
   ```

## Making Changes

1. **Write Tests**: Ensure your changes are covered by tests
2. **Update Documentation**: Keep documentation up to date with your changes
3. **Commit Messages**: Write clear, descriptive commit messages
4. **Pull Request**: Create a pull request when ready for review

## Testing

- Run all tests: `PYTHONPATH=src python -m unittest discover tests`
- If running tests for the first time: `sh prepare_for_tests.sh`

## Pull Request Process

1. Run all checks
2. Ensure all tests pass
3. Update documentation if needed
4. Request review from maintainers
5. Address any feedback
6. Merging has to be performed by the proponent, if he has the necessary privileges, otherwise from the maintainers

## Release Process

Run `sh release.sh`
