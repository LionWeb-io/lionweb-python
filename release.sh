#!/bin/bash

set -e  # Stop on errors

# Bump version
bump2version patch  # Change to minor or major if needed

# Push changes
git push origin --tags

rm -Rf dist

# Build the package
python -m build

# Upload to PyPI
twine upload --repository custom-pypi --config-file ~/.pypirc  --non-interactive dist/*
