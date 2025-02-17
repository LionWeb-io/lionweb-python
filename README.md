# LionWeb Python

[![PyPI version](https://img.shields.io/pypi/v/lionweb-python)](https://pypi.org/project/lionweb-python/)

This library contains an implementation in Python of the LionWeb specifications.

This library is released under the Apache V2 License.

## Linting

```
ruff check src/ tests/
mypy src/
```

## Formatting

```
black src/ tests/
isort src/ tests/
```

## Release process

```
pip install setuptools wheel twine
python setup.py sdist bdist_wheel
twine upload dist/* 
```
