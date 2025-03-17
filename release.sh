#!/bin/bash

set -e  # Stop on errors

# Bump version
bump2version patch  # Change to minor or major if needed

# Push changes
git push origin main --tags

# Build the package
python -m build

# Upload to PyPI
twine upload --repository custom-pypi --non-interactive dist/*
