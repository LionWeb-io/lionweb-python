#!/bin/bash
# Publishes a new release to PyPI. See "Release process" in README.md.
# Usage: ./release.sh [patch|minor|major]   (default: patch)

set -euo pipefail

PART="${1:-patch}"
case "$PART" in
  patch|minor|major) ;;
  *) echo "Usage: $0 [patch|minor|major]" >&2; exit 1 ;;
esac

# Only release an up-to-date, clean main
if [ "$(git branch --show-current)" != "main" ]; then
  echo "Releases must be made from main" >&2; exit 1
fi
if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
  echo "There are uncommitted changes" >&2; exit 1
fi
git fetch origin main --tags
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/main)" ]; then
  echo "Local main is not in sync with origin/main" >&2; exit 1
fi

# Bump version: commits and creates the vX.Y.Z tag
bump2version "$PART"
VERSION=$(sed -n 's/^current_version = //p' .bumpversion.cfg)

# Build the package
rm -Rf dist
python -m build
twine check dist/*

# Push the bump commit and the tag
git push origin main "v$VERSION"

# Upload to PyPI
twine upload --config-file ~/.pypirc --non-interactive dist/*
