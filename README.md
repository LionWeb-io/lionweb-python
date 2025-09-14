# LionWeb Python

[![PyPI version](https://img.shields.io/pypi/v/lionweb)](https://pypi.org/project/lionweb-python/)

This library contains an implementation in Python of the LionWeb specifications.

This library is released under the Apache V2 License.

Read the [Documentation](https://lionweb.io/lionweb-python)

We support Python 3.11 to 3.13

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

## Build locally

```
pip install build
python -m build
```

## Release process

* Update version in pyproject.toml and setup.py and src/lionwweb/__init__.py
* Create tag: `git tag -a v0.1.1 -m "Version 0.1.1"`
* Release on Pypi:

```
pip install setuptools wheel twine
python setup.py sdist bdist_wheel
twine upload dist/* 
```
* Push tag

## Tests

```
sh prepare_for_tests.sh # to be run just once
PYTHONPATH=src python -m unittest discover tests
```

You can measure coverage like this:
```
PYTHONPATH=src coverage run -m unittest discover tests
```

And then generate a report with:
```
coverage html                                         
# report generated under htmlcov/index.html
```

## Update Protobuffer classes

```
protoc --proto_path=./src --python_out=./src --mypy_out=./src -I . ./src/lionweb/serialization/proto/Chunk.proto 
```